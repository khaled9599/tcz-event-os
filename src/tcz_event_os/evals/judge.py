from tcz_event_os.domain.enums import Severity
from tcz_event_os.protocols.contracts import JudgeResult, ReviewFinding
class DeterministicJudge:
    id="independent_judge"
    def review(self,task,result):
        findings=[]
        if result.status.value not in {"submitted","passed"}: findings.append(ReviewFinding(code="status",severity=Severity.HIGH,message="Result not submitted."))
        if task.required_outputs and not result.outputs: findings.append(ReviewFinding(code="outputs",severity=Severity.HIGH,message="Required outputs missing."))
        if result.requires_human_decision: findings.append(ReviewFinding(code="human_gate",severity=Severity.MEDIUM,message="Human decision required before mutation."))
        passed=not any(f.severity in {Severity.HIGH,Severity.CRITICAL} for f in findings)
        return JudgeResult(task_id=task.id,reviewer_id=self.id,passed=passed,score=9.0 if passed and not findings else 7.0 if passed else 4.0,findings=findings)
