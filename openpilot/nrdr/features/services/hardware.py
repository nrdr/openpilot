from openpilot.common.version import sunnylink_consent_version, terms_version, terms_version_sp, training_version


def initialize_onboarding(params) -> None:
  params.put("HasAcceptedTerms", terms_version)
  params.put("HasAcceptedTermsSP", terms_version_sp)
  params.put("CompletedTrainingVersion", training_version)
  params.put("CompletedSunnylinkConsentVersion", sunnylink_consent_version)
  params.put_bool("SunnylinkEnabled", True)


def apply_startup_policy(startup_conditions: dict[str, bool]) -> None:
  startup_conditions["up_to_date"] = True
  startup_conditions["accepted_terms"] = True
  startup_conditions["accepted_terms_sp"] = True
  startup_conditions["completed_training"] = True


__all__ = ("apply_startup_policy", "initialize_onboarding")
