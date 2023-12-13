from dataclasses import dataclass


@dataclass
class JobValidation:
    valid_proposal_count: int
    valid_interviewing_count: int
    valid_invites_sent_count: int
    valid_elapsed_job_time: float
    valid_client_budget: float
    valid_hire_rate: float
    unsupported_country: list
    invalid_keywords: list
