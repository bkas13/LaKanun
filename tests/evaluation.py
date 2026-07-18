"""Evaluation framework for the legal classifier."""

import json
import logging
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from rich.console import Console
from rich.table import Table
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)

from src.classifier import LegalClassifier
from src.config import settings

logger = logging.getLogger(__name__)
console = Console()


@dataclass
class TestCase:
    """A single test case for evaluation."""

    id: str
    query: str
    country: str
    expected_classification: str
    expected_articles: List[str]
    expected_domains: List[str]
    difficulty: str  # easy, medium, hard
    language: str = "en"


@dataclass
class EvaluationResult:
    """Result of evaluating a single test case."""

    test_case: TestCase
    predicted_classification: str
    predicted_confidence: float
    predicted_articles: List[str]
    predicted_domains: List[str]
    response_time_ms: float
    classification_correct: bool
    article_precision_at_k: float
    domain_correct: bool


@dataclass
class EvaluationReport:
    """Complete evaluation report."""

    timestamp: str
    total_cases: int
    overall_accuracy: float
    accuracy_by_country: Dict[str, float]
    accuracy_by_domain: Dict[str, float]
    accuracy_by_difficulty: Dict[str, float]
    confusion_matrix: Dict
    classification_report: Dict
    avg_response_time_ms: float
    confidence_calibration: Dict
    article_retrieval_precision: Dict[int, float]
    failure_cases: List[Dict]


# ============================================================================
# TEST DATASETS
# ============================================================================

NEPAL_TEST_CASES = [
    # Clearly Legal (20)
    TestCase("np_legal_001", "A citizen votes in federal elections", "nepal", "legal",
             ["constitution_art_48"], ["constitutional"], "easy"),
    TestCase("np_legal_002", "A person practices Hinduism freely", "nepal", "legal",
             ["constitution_art_26"], ["fundamental_rights"], "easy"),
    TestCase("np_legal_003", "A journalist publishes an article criticizing government policy", "nepal", "legal",
             ["constitution_art_19"], ["fundamental_rights"], "easy"),
    TestCase("np_legal_004", "A worker joins a trade union", "nepal", "legal",
             ["constitution_art_34", "labor_act_2074"], ["fundamental_rights", "labor_law"], "easy"),
    TestCase("np_legal_005", "A couple registers their marriage at the ward office", "nepal", "legal",
             ["civil_code_2074"], ["family_law"], "easy"),
    TestCase("np_legal_006", "A person inherits ancestral property", "nepal", "legal",
             ["constitution_art_25", "civil_code_2074"], ["fundamental_rights", "property"], "easy"),
    TestCase("np_legal_007", "A citizen files RTI request for government information", "nepal", "legal",
             ["constitution_art_27", "rti_act"], ["fundamental_rights"], "easy"),
    TestCase("np_legal_008", "A person converts from Hinduism to Buddhism voluntarily", "nepal", "legal",
             ["constitution_art_26"], ["fundamental_rights"], "easy"),
    TestCase("np_legal_009", "A worker receives minimum wage as per government notification", "nepal", "legal",
             ["labor_act_2074", "minimum_wages"], ["labor_law"], "easy"),
    TestCase("np_legal_010", "A parent enrolls child in public school", "nepal", "legal",
             ["constitution_art_31"], ["fundamental_rights"], "easy"),
    TestCase("np_legal_011", "A person seeks healthcare at government hospital", "nepal", "legal",
             ["constitution_art_35"], ["fundamental_rights"], "easy"),
    TestCase("np_legal_012", "A citizen assembles peacefully with permit", "nepal", "legal",
             ["constitution_art_19"], ["fundamental_rights"], "easy"),
    TestCase("np_legal_013", "A person writes a will distributing property", "nepal", "legal",
             ["civil_code_2074"], ["property", "family_law"], "easy"),
    TestCase("np_legal_014", "A business registers company at OCR", "nepal", "legal",
             ["companies_act"], ["commercial"], "easy"),
    TestCase("np_legal_015", "A citizen obtains citizenship certificate", "nepal", "legal",
             ["constitution_art_53", "citizenship_act"], ["constitutional"], "easy"),
    TestCase("np_legal_016", "A person adopts a child through legal process", "nepal", "legal",
             ["civil_code_2074", "adoption_guidelines"], ["family_law"], "medium"),
    TestCase("np_legal_017", "A worker takes maternity leave as per law", "nepal", "legal",
             ["labor_act_2074", "constitution_art_38"], ["labor_law", "fundamental_rights"], "easy"),
    TestCase("np_legal_018", "A citizen files case in district court", "nepal", "legal",
             ["constitution_art_46", "civil_procedure"], ["fundamental_rights"], "easy"),
    TestCase("np_legal_019", "A person practices traditional medicine with license", "nepal", "legal",
             ["health_act"], ["health_law"], "medium"),
    TestCase("np_legal_020", "A farmer sells produce at market", "nepal", "legal",
             ["constitution_art_33", "agriculture_act"], ["fundamental_rights"], "easy"),

    # Clearly Illegal (20)
    TestCase("np_illegal_001", "An employer fires a worker without any notice", "nepal", "illegal",
             ["labor_act_2074_sec_114"], ["labor_law"], "easy"),
    TestCase("np_illegal_002", "A person discriminates against Dalit in hiring", "nepal", "illegal",
             ["constitution_art_18", "constitution_art_24", "caste_discrimination_act_2068"], ["fundamental_rights"], "easy"),
    TestCase("np_illegal_003", "Police arrest someone without warrant for minor offense", "nepal", "illegal",
             ["constitution_art_20", "criminal_procedure_code"], ["criminal", "fundamental_rights"], "easy"),
    TestCase("np_illegal_004", "A man forces his wife to bring dowry", "nepal", "illegal",
             ["penal_code_2074_sec_166", "constitution_art_38"], ["criminal", "fundamental_rights"], "easy"),
    TestCase("np_illegal_005", "A factory employs children under 14 in hazardous work", "nepal", "illegal",
             ["constitution_art_39", "labor_act_2074", "child_labor_act"], ["fundamental_rights", "labor_law"], "easy"),
    TestCase("np_illegal_006", "A person practices untouchability", "nepal", "illegal",
             ["constitution_art_24", "caste_discrimination_act_2068"], ["fundamental_rights"], "easy"),
    TestCase("np_illegal_007", "Government acquires land without compensation", "nepal", "illegal",
             ["constitution_art_25"], ["fundamental_rights", "property"], "medium"),
    TestCase("np_illegal_008", "An employer pays below minimum wage", "nepal", "illegal",
             ["labor_act_2074", "minimum_wages_act"], ["labor_law"], "easy"),
    TestCase("np_illegal_009", "A person traffics another for forced labor", "nepal", "illegal",
             ["constitution_art_29", "penal_code_2074", "human_trafficking_act"], ["criminal", "fundamental_rights"], "easy"),
    TestCase("np_illegal_010", "A husband practices polygamy", "nepal", "illegal",
             ["civil_code_2074", "penal_code_2074"], ["family_law", "criminal"], "easy"),
    TestCase("np_illegal_011", "A person marries a child under 20", "nepal", "illegal",
             ["civil_code_2074", "constitution_art_39"], ["family_law", "fundamental_rights"], "easy"),
    TestCase("np_illegal_012", "Police torture a suspect in custody", "nepal", "illegal",
             ["constitution_art_22", "penal_code_2074"], ["criminal", "fundamental_rights"], "easy"),
    TestCase("np_illegal_013", "An employer sexually harasses a worker", "nepal", "illegal",
             ["labor_act_2074", "sexual_harassment_act", "constitution_art_38"], ["labor_law", "criminal"], "medium"),
    TestCase("np_illegal_014", "A person sells banned drugs", "nepal", "illegal",
             ["drug_control_act", "penal_code_2074"], ["criminal"], "easy"),
    TestCase("np_illegal_015", "A company pollutes river without treatment", "nepal", "illegal",
             ["constitution_art_30", "environment_protection_act"], ["fundamental_rights", "environmental"], "medium"),
    TestCase("np_illegal_016", "A person forces religious conversion", "nepal", "illegal",
             ["constitution_art_26", "penal_code_2074"], ["fundamental_rights", "criminal"], "medium"),
    TestCase("np_illegal_017", "Government official takes bribe", "nepal", "illegal",
             ["penal_code_2074", "ciaa_act"], ["criminal"], "easy"),
    TestCase("np_illegal_018", "A person practices witchcraft accusation violence", "nepal", "illegal",
             ["penal_code_2074", "witchcraft_act"], ["criminal"], "medium"),
    TestCase("np_illegal_019", "An employer denies maternity leave", "nepal", "illegal",
             ["labor_act_2074", "constitution_art_38"], ["labor_law", "fundamental_rights"], "easy"),
    TestCase("np_illegal_020", "A person hacks into government database", "nepal", "illegal",
             ["electronic_transactions_act", "penal_code_2074"], ["criminal"], "medium"),

    # Conditional/Gray Area (10)
    TestCase("np_gray_001", "Police arrest without warrant for cognizable offense", "nepal", "illegal_with_conditions",
             ["criminal_procedure_code", "constitution_art_20"], ["criminal"], "medium"),
    TestCase("np_gray_002", "Employer terminates worker for proven gross misconduct", "nepal", "legal",
             ["labor_act_2074_sec_115"], ["labor_law"], "medium"),
    TestCase("np_gray_003", "Government restricts assembly during emergency", "nepal", "jurisdiction_specific",
             ["constitution_art_19", "constitution_art_281"], ["constitutional"], "hard"),
    TestCase("np_gray_004", "Person builds house on public land", "nepal", "illegal_with_conditions",
             ["constitution_art_25", "land_act"], ["property"], "medium"),
    TestCase("np_gray_005", "Religious institution restricts entry based on gender", "nepal", "gray_area",
             ["constitution_art_18", "constitution_art_26"], ["fundamental_rights"], "hard"),
    TestCase("np_gray_006", "Employer monitors employee emails on company system", "nepal", "gray_area",
             ["constitution_art_28", "labor_act_2074"], ["fundamental_rights", "labor_law"], "hard"),
    TestCase("np_gray_007", "Government surveils suspect with court order", "nepal", "legal",
             ["constitution_art_28", "criminal_procedure"], ["fundamental_rights", "criminal"], "medium"),
    TestCase("np_gray_008", "Person uses force in self-defense causing death", "nepal", "gray_area",
             ["penal_code_2074", "constitution_art_20"], ["criminal"], "hard"),
    TestCase("np_gray_009", "Media publishes classified info in public interest", "nepal", "gray_area",
             ["constitution_art_19", "constitution_art_27", "official_secrets_act"], ["fundamental_rights"], "hard"),
    TestCase("np_gray_010", "Foreigner buys land in Nepal", "nepal", "illegal_with_conditions",
             ["constitution_art_25", "land_act", "foreign_investment_act"], ["property"], "medium"),
]

INDIA_TEST_CASES = [
    # Clearly Legal (20)
    TestCase("in_legal_001", "A citizen votes in Lok Sabha elections", "india", "legal",
             ["constitution_art_326"], ["constitutional"], "easy"),
    TestCase("in_legal_002", "A person practices Islam freely", "india", "legal",
             ["constitution_art_25"], ["fundamental_rights"], "easy"),
    TestCase("in_legal_003", "A journalist publishes article criticizing government", "india", "legal",
             ["constitution_art_19_1_a"], ["fundamental_rights"], "easy"),
    TestCase("in_legal_004", "A worker forms a trade union", "india", "legal",
             ["constitution_art_19_1_c", "trade_unions_act"], ["fundamental_rights", "labor_law"], "easy"),
    TestCase("in_legal_005", "A couple registers marriage under Special Marriage Act", "india", "legal",
             ["special_marriage_act"], ["family_law"], "easy"),
    TestCase("in_legal_006", "A daughter inherits ancestral property equally", "india", "legal",
             ["hindu_succession_act_2005", "constitution_art_14"], ["family_law", "fundamental_rights"], "easy"),
    TestCase("in_legal_007", "A citizen files RTI application", "india", "legal",
             ["rti_act_2005", "constitution_art_19_1_a"], ["fundamental_rights"], "easy"),
    TestCase("in_legal_008", "A person converts religion voluntarily", "india", "legal",
             ["constitution_art_25"], ["fundamental_rights"], "easy"),
    TestCase("in_legal_009", "A worker receives minimum wages", "india", "legal",
             ["minimum_wages_act_1948"], ["labor_law"], "easy"),
    TestCase("in_legal_010", "A child receives free education under RTE", "india", "legal",
             ["constitution_art_21_a", "rte_act_2009"], ["fundamental_rights"], "easy"),
    TestCase("in_legal_011", "A person seeks treatment at government hospital", "india", "legal",
             ["constitution_art_21"], ["fundamental_rights"], "easy"),
    TestCase("in_legal_012", "Citizens assemble peacefully with permission", "india", "legal",
             ["constitution_art_19_1_b"], ["fundamental_rights"], "easy"),
    TestCase("in_legal_013", "A person writes a will", "india", "legal",
             ["indian_succession_act"], ["family_law", "property"], "easy"),
    TestCase("in_legal_014", "A company incorporates under Companies Act 2013", "india", "legal",
             ["companies_act_2013"], ["commercial"], "easy"),
    TestCase("in_legal_015", "A person obtains Aadhaar card", "india", "legal",
             ["aadhaar_act_2016"], ["administrative"], "easy"),
    TestCase("in_legal_016", "A couple adopts child under CARA guidelines", "india", "legal",
             ["juvenile_justice_act", "cara_regulations"], ["family_law"], "medium"),
    TestCase("in_legal_017", "A woman takes maternity leave under Maternity Benefit Act", "india", "legal",
             ["maternity_benefit_act_1961", "constitution_art_42"], ["labor_law", "fundamental_rights"], "easy"),
    TestCase("in_legal_018", "A citizen files writ petition in High Court", "india", "legal",
             ["constitution_art_226"], ["constitutional"], "easy"),
    TestCase("in_legal_019", "A doctor practices with valid MCI registration", "india", "legal",
             ["medical_council_act"], ["health_law"], "medium"),
    TestCase("in_legal_020", "A farmer sells produce at MSP", "india", "legal",
             ["constitution_art_19_1_g", "apmc_acts"], ["fundamental_rights"], "easy"),

    # Clearly Illegal (20)
    TestCase("in_illegal_001", "Employer terminates worker without notice", "india", "illegal",
             ["industrial_disputes_act_sec_25_f"], ["labor_law"], "easy"),
    TestCase("in_illegal_002", "Employer discriminates based on caste in hiring", "india", "illegal",
             ["constitution_art_15", "constitution_art_16", "sc_st_act_1989"], ["fundamental_rights"], "easy"),
    TestCase("in_illegal_003", "Police arrest without warrant for non-cognizable offense", "india", "illegal",
             ["crpc_sec_41", "constitution_art_22"], ["criminal", "fundamental_rights"], "easy"),
    TestCase("in_illegal_004", "Husband demands dowry from wife's family", "india", "illegal",
             ["dowry_prohibition_act_1961", "ipc_sec_498_a"], ["criminal", "family_law"], "easy"),
    TestCase("in_illegal_005", "Factory employs children under 14 in hazardous work", "india", "illegal",
             ["constitution_art_24", "child_labour_act_1986"], ["fundamental_rights", "labor_law"], "easy"),
    TestCase("in_illegal_006", "Person practices untouchability", "india", "illegal",
             ["constitution_art_17", "pcra_act_1955"], ["fundamental_rights"], "easy"),
    TestCase("in_illegal_007", "Government acquires land without fair compensation", "india", "illegal",
             ["constitution_art_300_a", "lrar_act_2013"], ["property", "constitutional"], "medium"),
    TestCase("in_illegal_008", "Employer pays below minimum wages", "india", "illegal",
             ["minimum_wages_act_1948"], ["labor_law"], "easy"),
    TestCase("in_illegal_009", "Person traffics another for forced labor", "india", "illegal",
             ["constitution_art_23", "ipc_sec_370", "immoral_traffic_act"], ["criminal", "fundamental_rights"], "easy"),
    TestCase("in_illegal_010", "Hindu man marries second wife while first alive", "india", "illegal",
             ["hmc_act_1955", "ipc_sec_494"], ["family_law", "criminal"], "easy"),
    TestCase("in_illegal_011", "Child marriage below 18/21 years", "india", "illegal",
             ["pcma_act_2006", "constitution_art_21"], ["family_law", "fundamental_rights"], "easy"),
    TestCase("in_illegal_012", "Police torture suspect in custody", "india", "illegal",
             ["constitution_art_21", "ipc_sec_330_331", "dk_basu_guidelines"], ["criminal", "fundamental_rights"], "easy"),
    TestCase("in_illegal_013", "Employer sexually harasses woman at workplace", "india", "illegal",
             ["posh_act_2013", "ipc_sec_354_a", "constitution_art_14_15_21"], ["criminal", "labor_law"], "medium"),
    TestCase("in_illegal_014", "Person sells narcotic drugs", "india", "illegal",
             ["ndps_act_1985"], ["criminal"], "easy"),
    TestCase("in_illegal_015", "Industry discharges untreated effluent into river", "india", "illegal",
             ["water_act_1974", "ep_act_1986", "constitution_art_21"], ["environmental", "fundamental_rights"], "medium"),
    TestCase("in_illegal_016", "Person forces religious conversion", "india", "illegal",
             ["constitution_art_25", "state_anti_conversion_laws"], ["fundamental_rights", "criminal"], "medium"),
    TestCase("in_illegal_017", "Public servant takes bribe", "india", "illegal",
             ["pc_act_1988", "ipc_sec_161_165"], ["criminal"], "easy"),
    TestCase("in_illegal_018", "Employer denies maternity benefit", "india", "illegal",
             ["maternity_benefit_act_1961"], ["labor_law"], "easy"),
    TestCase("in_illegal_019", "Person hacks government computer system", "india", "illegal",
             ["it_act_2000_sec_66", "ipc"], ["criminal"], "medium"),
    TestCase("in_illegal_020", "Triple talaq given to Muslim woman", "india", "illegal",
             ["muslim_women_act_2019", "constitution_art_14_15_21"], ["family_law", "fundamental_rights"], "easy"),

    # Conditional/Gray Area (10)
    TestCase("in_gray_001", "Police arrest without warrant for cognizable offense", "india", "illegal_with_conditions",
             ["crpc_sec_41", "constitution_art_22"], ["criminal"], "medium"),
    TestCase("in_gray_002", "Employer terminates for proven misconduct after inquiry", "india", "legal",
             ["industrial_disputes_act", "standing_orders"], ["labor_law"], "medium"),
    TestCase("in_gray_003", "Government restricts internet during emergency", "india", "jurisdiction_specific",
             ["constitution_art_19_2", "constitution_art_352_356"], ["constitutional"], "hard"),
    TestCase("in_gray_004", "Person encroaches on government land", "india", "illegal_with_conditions",
             ["constitution_art_300_a", "public_premises_act"], ["property"], "medium"),
    TestCase("in_gray_005", "Religious institution restricts entry based on gender", "india", "gray_area",
             ["constitution_art_14_15", "constitution_art_25_26", "sabarimala_judgment"], ["fundamental_rights"], "hard"),
    TestCase("in_gray_006", "Employer monitors employee emails on company system", "india", "gray_area",
             ["constitution_art_21", "it_act_2000", "puttaswamy_judgment"], ["fundamental_rights", "labor_law"], "hard"),
    TestCase("in_gray_007", "Government surveils with judicial authorization", "india", "legal",
             ["constitution_art_21", "puttaswamy_judgment", "telegraph_act"], ["fundamental_rights", "criminal"], "medium"),
    TestCase("in_gray_008", "Person uses force in self-defense causing death", "india", "gray_area",
             ["ipc_sec_96_106"], ["criminal"], "hard"),
    TestCase("in_gray_009", "Media publishes classified info in public interest", "india", "gray_area",
             ["constitution_art_19_1_a", "official_secrets_act", "rt_act"], ["fundamental_rights"], "hard"),
    TestCase("in_gray_010", "Foreigner buys agricultural land in India", "india", "illegal_with_conditions",
             ["constitution_art_300_a", "state_land_laws", "fema_1999"], ["property"], "medium"),
]


def get_all_test_cases() -> List[TestCase]:
    """Get all test cases."""
    return NEPAL_TEST_CASES + INDIA_TEST_CASES


def get_test_cases_by_country(country: str) -> List[TestCase]:
    """Get test cases for a specific country."""
    if country.lower() == "nepal":
        return NEPAL_TEST_CASES
    elif country.lower() == "india":
        return INDIA_TEST_CASES
    return []


# ============================================================================
# EVALUATION ENGINE
# ============================================================================

class LegalEvaluator:
    """Evaluate legal classifier performance."""

    def __init__(self, classifier: LegalClassifier = None, use_llm: bool = False):
        self.classifier = classifier or LegalClassifier(use_llm=use_llm)
        self.results: List[EvaluationResult] = []

    def evaluate_single(self, test_case: TestCase, top_k: int = 10) -> EvaluationResult:
        """Evaluate a single test case."""
        start_time = time.time()

        # Run classification
        analysis = self.classifier.classify(
            query=test_case.query,
            country=test_case.country,
            language=test_case.language,
            top_k=top_k,
        )

        response_time = (time.time() - start_time) * 1000

        # Extract predicted articles
        predicted_articles = [
            law.id for law in analysis.applicable_laws
        ]

        # Check classification correctness
        classification_correct = analysis.classification == test_case.expected_classification

        # Article retrieval precision@k
        expected_set = set(test_case.expected_articles)
        predicted_set = set(predicted_articles[:top_k])
        article_precision = len(expected_set & predicted_set) / len(predicted_set) if predicted_set else 0.0

        # Domain correctness
        expected_domains = set(test_case.expected_domains)
        predicted_domains = set(analysis.legal_domains)
        domain_correct = len(expected_domains & predicted_domains) > 0

        return EvaluationResult(
            test_case=test_case,
            predicted_classification=analysis.classification,
            predicted_confidence=analysis.confidence,
            predicted_articles=predicted_articles,
            predicted_domains=analysis.legal_domains,
            response_time_ms=response_time,
            classification_correct=classification_correct,
            article_precision_at_k=article_precision,
            domain_correct=domain_correct,
        )

    def evaluate_dataset(self, test_cases: List[TestCase], top_k: int = 10) -> List[EvaluationResult]:
        """Evaluate a full dataset."""
        results = []

        console.print(f"[bold]Evaluating {len(test_cases)} test cases...[/bold]")

        for test_case in test_cases:
            try:
                result = self.evaluate_single(test_case, top_k)
                results.append(result)

                status = "✅" if result.classification_correct else "❌"
                console.print(f"  {status} {test_case.id}: {test_case.expected_classification} -> {result.predicted_classification} ({result.predicted_confidence:.1%})")

            except Exception as e:
                logger.error(f"Evaluation failed for {test_case.id}: {e}")
                console.print(f"  ⚠️ {test_case.id}: ERROR - {e}")

        self.results = results
        return results

    def generate_report(self) -> EvaluationReport:
        """Generate comprehensive evaluation report."""
        if not self.results:
            raise ValueError("No evaluation results. Run evaluate_dataset first.")

        # Overall accuracy
        correct = sum(1 for r in self.results if r.classification_correct)
        total = len(self.results)
        overall_accuracy = correct / total if total > 0 else 0

        # By country
        by_country = {}
        for country in ["nepal", "india"]:
            country_results = [r for r in self.results if r.test_case.country == country]
            if country_results:
                by_country[country] = sum(1 for r in country_results if r.classification_correct) / len(country_results)

        # By domain
        by_domain = {}
        all_domains = set()
        for r in self.results:
            all_domains.update(r.test_case.expected_domains)
        for domain in all_domains:
            domain_results = [r for r in self.results if domain in r.test_case.expected_domains]
            if domain_results:
                by_domain[domain] = sum(1 for r in domain_results if r.classification_correct) / len(domain_results)

        # By difficulty
        by_difficulty = {}
        for diff in ["easy", "medium", "hard"]:
            diff_results = [r for r in self.results if r.test_case.difficulty == diff]
            if diff_results:
                by_difficulty[diff] = sum(1 for r in diff_results if r.classification_correct) / len(diff_results)

        # Confusion matrix
        y_true = [r.test_case.expected_classification for r in self.results]
        y_pred = [r.predicted_classification for r in self.results]
        labels = sorted(set(y_true) | set(y_pred))
        cm = confusion_matrix(y_true, y_pred, labels=labels)
        cm_dict = {labels[i]: {labels[j]: int(cm[i, j]) for j in range(len(labels))} for i in range(len(labels))}

        # Classification report
        clf_report = classification_report(y_true, y_pred, labels=labels, output_dict=True, zero_division=0)

        # Avg response time
        avg_time = np.mean([r.response_time_ms for r in self.results])

        # Confidence calibration
        conf_bins = np.linspace(0, 1, 11)
        calibration = {}
        for i in range(len(conf_bins) - 1):
            low, high = conf_bins[i], conf_bins[i + 1]
            bin_results = [r for r in self.results if low <= r.predicted_confidence < high]
            if bin_results:
                acc = sum(1 for r in bin_results if r.classification_correct) / len(bin_results)
                avg_conf = np.mean([r.predicted_confidence for r in bin_results])
                calibration[f"{low:.1f}-{high:.1f}"] = {
                    "count": len(bin_results),
                    "accuracy": acc,
                    "avg_confidence": avg_conf,
                    "gap": avg_conf - acc,
                }

        # Article retrieval precision@k
        article_precision = {}
        for k in [1, 3, 5, 10]:
            precisions = [r.article_precision_at_k for r in self.results if r.test_case.expected_articles]
            article_precision[k] = np.mean(precisions) if precisions else 0.0

        # Failure cases
        failures = [
            {
                "id": r.test_case.id,
                "query": r.test_case.query[:100],
                "expected": r.test_case.expected_classification,
                "predicted": r.predicted_classification,
                "confidence": r.predicted_confidence,
                "country": r.test_case.country,
                "difficulty": r.test_case.difficulty,
            }
            for r in self.results if not r.classification_correct
        ]
        failures.sort(key=lambda x: -x["confidence"])

        return EvaluationReport(
            timestamp=datetime.utcnow().isoformat(),
            total_cases=total,
            overall_accuracy=overall_accuracy,
            accuracy_by_country=by_country,
            accuracy_by_domain=by_domain,
            accuracy_by_difficulty=by_difficulty,
            confusion_matrix=cm_dict,
            classification_report=clf_report,
            avg_response_time_ms=avg_time,
            confidence_calibration=calibration,
            article_retrieval_precision=article_precision,
            failure_cases=failures[:20],  # Top 20 failures
        )

    def print_report(self, report: EvaluationReport):
        """Print formatted evaluation report."""
        console.print("\n" + "=" * 60)
        console.print("[bold]EVALUATION REPORT[/bold]")
        console.print("=" * 60)

        console.print(f"\n📊 **Overall Accuracy:** {report.overall_accuracy:.1%} ({report.total_cases} cases)")
        console.print(f"⏱️  **Avg Response Time:** {report.avg_response_time_ms:.0f}ms")

        # By country
        console.print("\n[bold]Accuracy by Country:[/bold]")
        for country, acc in report.accuracy_by_country.items():
            console.print(f"  {country.upper()}: {acc:.1%}")

        # By domain
        console.print("\n[bold]Accuracy by Legal Domain:[/bold]")
        for domain, acc in sorted(report.accuracy_by_domain.items(), key=lambda x: -x[1]):
            console.print(f"  {domain}: {acc:.1%}")

        # By difficulty
        console.print("\n[bold]Accuracy by Difficulty:[/bold]")
        for diff, acc in report.accuracy_by_difficulty.items():
            console.print(f"  {diff}: {acc:.1%}")

        # Article retrieval
        console.print("\n[bold]Article Retrieval Precision@k:[/bold]")
        for k, prec in report.article_retrieval_precision.items():
            console.print(f"  P@{k}: {prec:.1%}")

        # Confidence calibration
        console.print("\n[bold]Confidence Calibration:[/bold]")
        cal_table = Table()
        cal_table.add_column("Confidence Bin")
        cal_table.add_column("Count")
        cal_table.add_column("Accuracy")
        cal_table.add_column("Avg Conf")
        cal_table.add_column("Gap")
        for bin_name, stats in report.confidence_calibration.items():
            cal_table.add_row(
                bin_name,
                str(stats["count"]),
                f"{stats['accuracy']:.1%}",
                f"{stats['avg_confidence']:.1%}",
                f"{stats['gap']:+.1%}",
            )
        console.print(cal_table)

        # Confusion matrix
        console.print("\n[bold]Confusion Matrix:[/bold]")
        cm_labels = list(report.confusion_matrix.keys())
        cm_table = Table()
        cm_table.add_column("")
        for label in cm_labels:
            cm_table.add_column(label)
        for true_label in cm_labels:
            row = [true_label]
            for pred_label in cm_labels:
                row.append(str(report.confusion_matrix[true_label].get(pred_label, 0)))
            cm_table.add_row(*row)
        console.print(cm_table)

        # Top failures
        if report.failure_cases:
            console.print("\n[bold red]Top Failure Cases (High Confidence Errors):[/bold red]")
            for i, fail in enumerate(report.failure_cases[:10], 1):
                console.print(f"  {i}. [{fail['country'].upper()}] {fail['query']}")
                console.print(f"     Expected: {fail['expected']} | Got: {fail['predicted']} (conf: {fail['confidence']:.1%})")

    def save_report(self, report: EvaluationReport, filepath: Path):
        """Save report to JSON and Markdown."""
        # JSON
        json_path = filepath.with_suffix(".json")
        with open(json_path, "w") as f:
            json.dump(asdict(report), f, indent=2, default=str)

        # Markdown
        md_path = filepath.with_suffix(".md")
        with open(md_path, "w") as f:
            f.write(f"# Legal Classifier Evaluation Report\n\n")
            f.write(f"**Generated:** {report.timestamp}\n\n")
            f.write(f"## Summary\n\n")
            f.write(f"- **Total Cases:** {report.total_cases}\n")
            f.write(f"- **Overall Accuracy:** {report.overall_accuracy:.1%}\n")
            f.write(f"- **Avg Response Time:** {report.avg_response_time_ms:.0f}ms\n\n")

            f.write(f"## Accuracy by Country\n\n")
            for country, acc in report.accuracy_by_country.items():
                f.write(f"- **{country.upper()}:** {acc:.1%}\n")

            f.write(f"\n## Accuracy by Legal Domain\n\n")
            for domain, acc in sorted(report.accuracy_by_domain.items(), key=lambda x: -x[1]):
                f.write(f"- **{domain}:** {acc:.1%}\n")

            f.write(f"\n## Accuracy by Difficulty\n\n")
            for diff, acc in report.accuracy_by_difficulty.items():
                f.write(f"- **{diff}:** {acc:.1%}\n")

            f.write(f"\n## Article Retrieval Precision@k\n\n")
            for k, prec in report.article_retrieval_precision.items():
                f.write(f"- **P@{k}:** {prec:.1%}\n")

            f.write(f"\n## Confidence Calibration\n\n")
            f.write("| Bin | Count | Accuracy | Avg Conf | Gap |\n")
            f.write("|-----|-------|----------|----------|-----|\n")
            for bin_name, stats in report.confidence_calibration.items():
                f.write(f"| {bin_name} | {stats['count']} | {stats['accuracy']:.1%} | {stats['avg_confidence']:.1%} | {stats['gap']:+.1%} |\n")

            f.write(f"\n## Top Failure Cases\n\n")
            for i, fail in enumerate(report.failure_cases[:10], 1):
                f.write(f"{i}. **[{fail['country'].upper()}]** {fail['query']}\n")
                f.write(f"   - Expected: {fail['expected']} | Predicted: {fail['predicted']} (conf: {fail['confidence']:.1%})\n\n")

        console.print(f"\n💾 Report saved to {json_path} and {md_path}")


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate legal classifier")
    parser.add_argument("--country", choices=["nepal", "india", "both"], default="both")
    parser.add_argument("--use-llm", action="store_true", help="Use LLM for classification")
    parser.add_argument("--top-k", type=int, default=10, help="Top k articles for retrieval")
    parser.add_argument("--output", type=str, default="tests/evaluation_report", help="Output path")
    parser.add_argument("--quick", action="store_true", help="Run quick evaluation (first 10 per country)")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    # Get test cases
    if args.country == "nepal":
        test_cases = NEPAL_TEST_CASES
    elif args.country == "india":
        test_cases = INDIA_TEST_CASES
    else:
        test_cases = NEPAL_TEST_CASES + INDIA_TEST_CASES

    if args.quick:
        test_cases = test_cases[:20]

    # Run evaluation
    evaluator = LegalEvaluator(use_llm=args.use_llm)
    evaluator.evaluate_dataset(test_cases, top_k=args.top_k)

    # Generate and print report
    report = evaluator.generate_report()
    evaluator.print_report(report)

    # Save
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    evaluator.save_report(report, output_path)


if __name__ == "__main__":
    main()