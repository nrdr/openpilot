#pragma once

#include "selfdrive/ui/qt/onroad/annotated_camera.h"

class StarPilotOnroadWindow : public QWidget {
  Q_OBJECT

public:
  StarPilotOnroadWindow(QWidget* parent = 0);

  void updateState(const UIState &s, const StarPilotUIState &fs);

  float fps;

  StarPilotUIScene starpilot_scene;

  QColor bg;

  QJsonObject starpilot_toggles;

private:
  void paintEvent(QPaintEvent *event);
  void paintFPS(QPainter &p);
  void paintSteeringTorqueBorder(QPainter &p);
  void paintTurnSignalBorder(QPainter &p);
  void resizeEvent(QResizeEvent *event);

  bool blindSpotLeft;
  bool blindSpotRight;
  bool flickerActive;
  bool showBlindspot;
  bool showFPS;
  bool showSignal;
  bool showSteering;
  bool turnSignalLeft;
  bool turnSignalRight;

  float smoothedSteer;
  float torque;

  QColor leftBorderColor;
  QColor rightBorderColor;

  QRect rect;
  QLinearGradient steeringGradient;

  QRegion marginRegion;

  QString fpsDisplayString;

  QTimer *signalTimer;
};
