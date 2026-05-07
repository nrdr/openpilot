#pragma once

#include "starpilot/ui/qt/offroad/starpilot_settings.h"

class StarPilotVisualsPanel : public StarPilotListWidget {
  Q_OBJECT

public:
  explicit StarPilotVisualsPanel(StarPilotSettingsWindow *parent, bool forceOpen = false);

signals:
  void openSubPanel();
  void openSubSubPanel();

protected:
  void showEvent(QShowEvent *event) override;

private:
  void updateMetric(bool metric, bool bootRun);
  void updateToggles();

  bool forceOpenDescriptions;

  std::map<QString, AbstractControl*> toggles;

  QSet<QString> advancedCustomOnroadUIKeys = {"HideAlerts", "HideChangingLanesBanner", "HideDistanceProfileBanner", "HideDMIcon", "HideLeadMarker", "HideMaxSpeed", "HideSpeed", "HideSpeedLimit", "HideSteeringWheel", "HideTurningBanner", "WheelSpeed"};
  QSet<QString> customOnroadUIKeys = {"AccelerationPath", "AdjacentPath", "BlindSpotPath", "Compass", "OnroadDistanceButton", "PedalsOnUI", "RotatingWheel"};
  QSet<QString> modelUIKeys = {"DynamicPathWidth", "LaneLinesWidth", "PathEdgeWidth", "PathWidth", "RoadEdgesWidth"};
  QSet<QString> navigationUIKeys = {"RoadNameUI", "ShowSpeedLimits", "SLCMapboxFiller", "UseVienna"};
  QSet<QString> qualityOfLifeKeys = {"CameraView", "DriverCamera", "StoppedTimer"};

  QSet<QString> parentKeys;

  StarPilotSettingsWindow *parent;

  Params params;
};
