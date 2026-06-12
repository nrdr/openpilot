import os

from openpilot.common.api.base import BaseApi

# nrdr: default to konik so registration routes correctly regardless of how the
# boot chain launches manager (the launch_env.sh export is not sourced on this
# base). build_prebuilt.sh reverts this to comma for the clean branch.
API_HOST = os.getenv('API_HOST', 'https://api.konik.ai')


class CommaConnectApi(BaseApi):
  def __init__(self, dongle_id):
    super().__init__(dongle_id, API_HOST)
    self.user_agent = "openpilot-"
