#pragma once

#include "selfdrive/ui/qt/onroad/buttons.h"
#include "selfdrive/ui/qt/widgets/cameraview.h"

const int widget_size = img_size + (UI_BORDER_SIZE / 2);

class StarPilotAnnotatedCameraWidget : public QWidget {
  Q_OBJECT

public:
  explicit StarPilotAnnotatedCameraWidget(QWidget *parent = 0);

  void mousePressEvent(QMouseEvent *mouseEvent) override;
  void paintAdjacentPaths(QPainter &p);
  void paintBlindSpotPath(QPainter &p);
  void paintStarPilotWidgets(QPainter &p, UIState &s);
  void paintLeadMetrics(QPainter &p, bool adjacent, QPointF *chevron, const cereal::RadarState::LeadData::Reader &lead_data);
  void paintPathEdges(QPainter &p, int height);
  void paintRainbowPath(QPainter &p, QLinearGradient &bg, float lin_grad_point);
  void updateState(const UIState &s, const StarPilotUIState &fs);

  bool hideBottomIcons;
  bool isCruiseSet;
  bool rightHandDM;

  int alertHeight;
  int speedLimitHeight;
  int standstillDuration;

  float speed;

  std::vector<QPointF> radar_tracks;

  StarPilotUIScene starpilot_scene;

  QColor blueColor(int alpha = 255) { return QColor(0, 0, 255, alpha); }
  QColor purpleColor(int alpha = 255) { return QColor(128, 0, 128, alpha); }
  QColor whiteColor(int alpha = 255) { return QColor(255, 255, 255, alpha); }

  QJsonObject starpilot_toggles;

  QPoint dmIconPosition;
  QPoint experimentalButtonPosition;

  QPolygonF track_adjacent_vertices[2];
  QPolygonF track_edge_vertices;
  QPolygonF track_vertices;

  QRect adjacentLeadTextRect;
  QRect leadTextRect;
  QRect setSpeedRect;

  QSize defaultSize;

  QString signalStyle;

protected:
  void showEvent(QShowEvent *event) override;

private:
  void paintCEMStatus(QPainter &p);
  void paintCompass(QPainter &p);
  void paintCurveSpeedControl(QPainter &p);
  void paintCurveSpeedControlTraining(QPainter &p);
  void paintLateralPaused(QPainter &p);
  void paintLongitudinalPaused(QPainter &p);
  void paintPedalIcons(QPainter &p);
  void paintPendingSpeedLimit(QPainter &p);
  void paintRadarTracks(QPainter &p);
  void paintRoadName(QPainter &p);
  void paintSpeedLimit(QPainter &p);
  void paintSpeedLimitSources(QPainter &p);
  void paintStandstillTimer(QPainter &p);
  void paintForceStop(QPainter &p);
  void paintStoppingPoint(QPainter &p);
  void paintTurnSignals(QPainter &p);
  void paintWeather(QPainter &p);
  void updateSignals();

  bool blindspotLeft;
  bool blindspotRight;
  bool blinkerLeft;
  bool blinkerRight;
  bool brakeLights;
  bool cscControllingSpeed;
  bool forcingStop;
  bool stopSignConfirmed;
  bool cscTraining;
  bool experimentalMode;
  bool forceCoast;
  bool lateralPaused;
  bool longitudinalPaused;
  bool redLight;
  bool speedLimitChanged;
  bool weatherDaytime;

  // Cached toggle values — refreshed once per updateState(), used in paint code
  bool cachedAdjacentPathMetrics = false;
  bool cachedBlindSpotPath = false;
  bool cachedCemStatus = false;
  bool cachedCompass = false;
  bool cachedCscStatus = false;
  bool cachedDynamicPedalsOnUi = false;
  bool cachedHideSpeedLimit = false;
  bool cachedOpenpilotLongitudinal = false;
  bool cachedPedalsOnUi = false;
  bool cachedRadarTracks = false;
  bool cachedRoadNameUi = false;
  bool cachedShowSpeedLimitOffset = false;
  bool cachedShowSpeedLimits = false;
  bool cachedShowStoppingPoint = false;
  bool cachedShowStoppingPointMetrics = false;
  bool cachedSimpleMode = false;
  bool cachedSpeedLimitController = false;
  bool cachedSpeedLimitSources = false;
  bool cachedSpeedLimitVienna = false;
  bool cachedStaticPedalsOnUi = false;
  bool cachedStoppedTimer = false;
  double cachedLaneDetectionWidth = 3.7;
  QString cachedColorScheme;
  QString cachedPathEdgesColor;
  QString cachedSignalIcons;

  int animationFrameIndex;
  int desiredFollowDistance;
  int frogHopCount;
  int signalAnimationLength;
  int signalHeight;
  int signalMovement;
  int signalWidth;
  int totalFrames;
  int weatherId;

  float accelerationEgo;
  float cscSpeed;
  float forcingStopLength;
  float dashboardSpeedLimit;
  float distanceConversion;
  float laneWidthLeft;
  float laneWidthRight;
  float mapSpeedLimit;
  float mapboxSpeedLimit;
  float nextSpeedLimit;
  float roadCurvature;
  float setSpeed;
  float slcOverriddenSpeed;
  float speedConversion;
  float speedConversionMetrics;
  float speedLimit;
  float stoppingDistance;
  float unconfirmedSpeedLimit;
  float visionSpeedLimit;

  std::string speedLimitSource;

  Params params;
  Params params_memory{"", true};

  QColor blackColor(int alpha = 255) { return QColor(0, 0, 0, alpha); }
  QColor redColor(int alpha = 255) { return QColor(201, 34, 49, alpha); }

  QElapsedTimer glowTimer;
  QElapsedTimer pendingLimitTimer;
  QElapsedTimer standstillTimer;

  QPixmap brakePedalImg;
  QPixmap curveSpeedIcon;
  QPixmap curveSpeedIconFlipped;
  QPixmap dashboardIcon;
  QPixmap gasPedalImg;
  QPixmap mapboxIcon;
  QPixmap mapDataIcon;
  QPixmap nextMapsIcon;
  QPixmap pausedIcon;
  QPixmap speedIcon;
  QPixmap forceStopDashImg;
  QPixmap forceStopImg;
  QPixmap stopSignImg;
  QPixmap turnIcon;
  QPixmap visionIcon;

  QPoint cemStatusPosition;
  QPoint compassPosition;
  QPoint lateralPausedPosition;

  QRect newSpeedLimitRect;
  QRect speedLimitRect;

  QSharedPointer<QMovie> cemCurveIcon;
  QSharedPointer<QMovie> cemLeadIcon;
  QSharedPointer<QMovie> cemSpeedIcon;
  QSharedPointer<QMovie> cemStopIcon;
  QSharedPointer<QMovie> cemTurnIcon;
  QSharedPointer<QMovie> chillModeIcon;
  QSharedPointer<QMovie> experimentalModeIcon;
  QSharedPointer<QMovie> weatherClearDay;
  QSharedPointer<QMovie> weatherClearNight;
  QSharedPointer<QMovie> weatherLowVisibility;
  QSharedPointer<QMovie> weatherRain;
  QSharedPointer<QMovie> weatherSnow;

  QString leadDistanceUnit;
  QString leadSpeedUnit;
  QString roadName;
  QString speedLimitOffsetStr;
  QString speedUnit;

  QTimer *animationTimer;

  QVector<QPixmap> blindspotImages;
  QVector<QPixmap> blindspotImagesRight;
  QVector<QPixmap> signalImages;
  QVector<QPixmap> signalImagesRight;
};
