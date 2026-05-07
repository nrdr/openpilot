#include "starpilot/ui/qt/onroad/starpilot_onroad.h"

StarPilotOnroadWindow::StarPilotOnroadWindow(QWidget *parent) : QWidget(parent) {
  signalTimer = new QTimer(this);
  QObject::connect(signalTimer, &QTimer::timeout, [this] {
    flickerActive = !flickerActive;
  });
}

void StarPilotOnroadWindow::resizeEvent(QResizeEvent *event) {
  rect = QWidget::rect();
  marginRegion = QRegion(rect) - QRegion(rect.marginsRemoved(QMargins(UI_BORDER_SIZE, UI_BORDER_SIZE, UI_BORDER_SIZE, UI_BORDER_SIZE)));

  steeringGradient = QLinearGradient(rect.topLeft(), rect.bottomLeft());
  QColor bottomGreen = bg_colors[STATUS_ENGAGED].lighter(120);
  bottomGreen.setAlpha(bg_colors[STATUS_ENGAGED].alpha());
  steeringGradient.setColorAt(0.0, bg_colors[STATUS_TRAFFIC_MODE_ENABLED]);
  steeringGradient.setColorAt(0.25, bg_colors[STATUS_EXPERIMENTAL_MODE_ENABLED]);
  steeringGradient.setColorAt(0.5, bg_colors[STATUS_CEM_DISABLED]);
  steeringGradient.setColorAt(0.75, bg_colors[STATUS_ENGAGED]);
  steeringGradient.setColorAt(1.0, bottomGreen);
}

void StarPilotOnroadWindow::updateState(const UIState &s, const StarPilotUIState &fs) {
  const SubMaster &sm = *(s.sm);
  const SubMaster &fpsm = *(fs.sm);

  const cereal::CarState::Reader &carState = sm["carState"].getCarState();
  const cereal::CarControl::Reader &carControl = fpsm["carControl"].getCarControl();

  blindSpotLeft = carState.getLeftBlindspot();
  blindSpotRight = carState.getRightBlindspot();
  torque = -carControl.getActuators().getTorque();
  turnSignalLeft = carState.getLeftBlinker();
  turnSignalRight = carState.getRightBlinker();

  showBlindspot = (blindSpotLeft || blindSpotRight) && starpilot_toggles.value("blind_spot_metrics").toBool();
  showFPS = starpilot_toggles.value("show_fps").toBool();
  showSignal = (turnSignalLeft || turnSignalRight) && starpilot_toggles.value("signal_metrics").toBool();
  showSteering = starpilot_toggles.value("steering_metrics").toBool();

  if (showSteering) {
    float absTorque = std::abs(torque);
    smoothedSteer = 0.25f * absTorque + 0.75f * smoothedSteer;
    if (std::abs(smoothedSteer - absTorque) < 0.01f) {
      smoothedSteer = absTorque;
    }
  }

  if (showBlindspot || showSignal) {
    std::function<QColor(bool, bool)> getBorderColor = [&](bool blindSpot, bool turnSignal) {
      if (turnSignal && showSignal) {
        if (blindSpot) {
          return flickerActive ? bg_colors[STATUS_TRAFFIC_MODE_ENABLED] : bg_colors[STATUS_CEM_DISABLED];
        } else {
          return flickerActive ? bg_colors[STATUS_CEM_DISABLED] : bg;
        }
      } else if (blindSpot && showBlindspot) {
        return bg_colors[STATUS_TRAFFIC_MODE_ENABLED];
      } else {
        return bg;
      }
    };

    leftBorderColor = getBorderColor(blindSpotLeft, turnSignalLeft);
    rightBorderColor = getBorderColor(blindSpotRight, turnSignalRight);

    int interval = showBlindspot ? 250 : 500;
    if (!signalTimer->isActive() || signalTimer->interval() != interval) {
      signalTimer->start(interval);
    }
  } else if (signalTimer->isActive()) {
    signalTimer->stop();
  }

  if (showFPS) {
    static float avgFPS = 0.0f;
    static float maxFPS = 0.0f;
    static float minFPS = 99.9f;

    if (avgFPS == 0.0f) {
      avgFPS = fps;
    }

    static float alpha = 1.0f / (UI_FREQ * 60.0f);
    avgFPS = alpha * fps + (1.0f - alpha) * avgFPS;

    minFPS = std::min(minFPS, fps);
    maxFPS = std::max(maxFPS, fps);

    fpsDisplayString = QString("FPS: %1 | Min: %2 | Max: %3 | Avg: %4")
                          .arg(qRound(fps))
                          .arg(qRound(minFPS))
                          .arg(qRound(maxFPS))
                          .arg(qRound(avgFPS));
  }

  if (showBlindspot || showSignal || showSteering || showFPS) {
    update();
  }
}

void StarPilotOnroadWindow::paintEvent(QPaintEvent *event) {
  QPainter p(this);

  p.setClipRegion(marginRegion);
  p.setRenderHints(QPainter::Antialiasing | QPainter::TextAntialiasing);

  if (showSteering) {
    paintSteeringTorqueBorder(p);
  }

  if (showBlindspot || showSignal) {
    paintTurnSignalBorder(p);
  }

  if (showFPS) {
    paintFPS(p);
  }
}

void StarPilotOnroadWindow::paintFPS(QPainter &p) {
  p.save();

  p.setFont(InterFont(28, QFont::DemiBold));
  p.setPen(Qt::white);

  int xPos = (rect.width() - p.fontMetrics().horizontalAdvance(fpsDisplayString)) / 2;
  int yPos = rect.bottom() - 5;

  p.drawText(xPos, yPos, fpsDisplayString);

  p.restore();
}

void StarPilotOnroadWindow::paintSteeringTorqueBorder(QPainter &p) {
  p.save();

  int visibleHeight = rect.height() * smoothedSteer;
  int xPos = (torque < 0) ? rect.x() : (rect.x() + rect.width() - UI_BORDER_SIZE);
  int yPos = rect.y() + rect.height() - visibleHeight;

  p.fillRect(QRect(xPos, yPos, UI_BORDER_SIZE, visibleHeight), steeringGradient);

  p.restore();
}

void StarPilotOnroadWindow::paintTurnSignalBorder(QPainter &p) {
  p.save();

  p.fillRect(rect.x(), rect.y(), rect.width() / 2, rect.height(), leftBorderColor);
  p.fillRect(rect.x() + rect.width() / 2, rect.y(), rect.width() / 2, rect.height(), rightBorderColor);

  p.restore();
}
