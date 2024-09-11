from app.services.llm_factory import LlmFactory
from app.services.prompts import (
    DISCLAIMER_PAGE_CLASSIFICATION_PROMPT,
    STANDARD_TEXT_CLASSIFICATION_PROMPT,
)
from typing import Dict
import json
from abc import ABC, abstractmethod


class BaseClassifier(ABC):
    def __init__(self, provider: str = "azure-openai"):
        self._provider = provider
        self._llm = LlmFactory(self._provider)

    @abstractmethod
    def get_prompt(self) -> Dict[str, str]:
        pass

    def classify(self, text: str, model) -> Dict[str, int]:
        prompt = self.get_prompt()
        messages = [
            {"role": "system", "content": prompt["system"]},
            {
                "role": "user",
                "content": prompt["user"].format(text=text),
            },
        ]
        params = {"model": model, "messages": messages, "temperature": 0.2}
        if self._provider == "azure-openai":
            params["response_format"] = {"type": "json_object"}
        else:
            params["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": "classification_response",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {"exclude": {"type": "integer"}},
                        "required": ["exclude"],
                    },
                },
            }
        completion = self._llm.create_completion(**params)

        response = completion.choices[0].message.content
        classification = json.loads(response)
        return classification


class DisclaimerPageClassifier(BaseClassifier):
    def get_prompt(self) -> Dict[str, str]:
        return DISCLAIMER_PAGE_CLASSIFICATION_PROMPT


class StatementExerptClassifier(BaseClassifier):
    def get_prompt(self) -> Dict[str, str]:
        return STANDARD_TEXT_CLASSIFICATION_PROMPT


# Example usage
if __name__ == "__main__":
    # python -m app.services.text_cleanup.text_classification.llm
    sample_disclaimer_text = """# Additional Information
    We have an introducing broker/carrying broker agreement with National Bank Financial Inc. (NBF Inc.), through its National Bank Independent Network (NBIN) division. Under such agreement, NBIN may provide us with custody, trading, clearing and settlement services. As the Introducing Broker, we are responsible for determining and supervising the suitability of trading activity, and the opening and initial approval of accounts.
    We have an introducing broker/carrying broker agreement with National Bank Financial Inc. (NBF Inc.), through its National Bank Independent Network (NBIN) division. Under such agreement, NBIN may provide us with custody, trading, clearing and settlement services. As the Introducing Broker, we are responsible for determining and supervising the suitability of trading activity, and the opening and initial approval of accounts.

    Please review your Investment Portfolio Statement . Any errors should be reported to our Compliance Department in writing within 30 days. For additional information, please speak to your Investment Advisor.

    We are required to disclose to Canada Revenue Agency all transactions involving the disposition of securities, even if no tax forms are produced for such dispositions. Please keep your statement as a reference for tax purposes.

    Customers' accounts are protected by the Canadian Investor Protection Fund within specified limits. A brochure describing the nature and limits of coverage is available upon request or at www.cipf.ca.

    Copies of our financial position as of our most recent financial year-end and a list of our directors and senior officers are available upon written request.

    Any free credit balances represent funds payable on demand which, although properly recorded on our books, are not segregated and may be used in the conduct of our business. Cash balances in registered accounts are held in trust by the plan trustee Natcan Trust Company, a subsidiary of National Bank of Canada.


    ## Portfolio Summary

    The amounts shown in this section are given in Canadian dollars.

    The subsection on Asset Allocation indicates how the consolidated financial assets you hold with us are distributed across each of the basic asset classes. Any securities sold short or debit cash positions are excluded from this asset mix calculation.


    ## Detailed Information per account

    The Cash Flow Summary subsection presents changes in your cash balance during the period. Amounts are shown in the currency of the account in broader categories for current period and for the calendar year to date.

    Interest rates on debit and credit balances are available upon request, please contact your Investment Advisor.

    Using borrowed money to finance the purchase of securities involves greater risk than using cash resources only. If you borrow money to purchase securities, your responsibility to repay the loan and pay interest as required by its terms remains the same even if the value of the securities purchased declines.

    The Asset Details subsection provides a listing of the securities you hold in the account, by asset class.

    The "Status" column provides information on how securities in your accounts are held. "SEG" (segregated) indicates fully paid securities which are segregated and held for you in nominee form. "SFK" (safekeeping) indicates fully paid securities, which are segregated and held registered in your name. "OWED" indicates securities you have sold but which have not yet been delivered to us, or securities that were sold short. "UNSG" (unsegregated) indicates securities being held as collateral for your margin loan, and are therefore not segregated.

    The "Book Cost" column means (i) In the case of a long security position, the total amount paid for the security, including any transaction charges related to the purchase, adjusted for reinvested distributions , returns of capital and corporate actions; or (ii) In the case of a short security position, the total amount received for the security, net of any transaction charges related to the sale, adjusted for any distributions (other than dividends), returns of capital and corporate actions.

    We do not guarantee the accuracy of the book costs and market values since they may have been acquired from an external source. You accept responsibility for the accuracy of these values and their use for tax reporting purposes. Where no book cost or market value is available, N/A is displayed on your statement.

    The Activity Details subsection presents, in chronological order, all transactions made during the period.

    All dates of transactions are settlement dates.

    Purchases and/or dispositions of securities resulting from transactions settled after month-end will be reflected in the following month's Portfolio Statement.


    # Footnotes

    Following footnotes may be shown in the Asset Details section.

    (1) Non determinable price: This indicates that the current market value for a particular security was not available at the time the statement was produced. For valuation purposes, a price of zero is applied. In the future, should the market value become available, it will be used, replacing this indicator.

    (2) Book cost at market value: this indicates that information on the book value for a particular security is not available or incomplete and the current market value was used to estimate all or part of the book value.

    (3) Deferred sales charge: This indicates that the security was purchased on a deferred sales charge (DSC) basis. Depending on the number of years it is held, charges may be applied by the issuer when the security is sold.

    (4) Accrued interest: This indicates, whenever possible, that market values for fixed-income securities include accrued interest.

    (5) Estimated value: This indicates, in the case of securities not listed on an exchange or traded infrequently, the value given is an estimate which does not necessarily reflect the actual market value.


    ## Abbreviations

    The following is a list of the main abbreviations that may appear on your statement to identify share classes.

    |||
    | - | - |
    | Share classes NVS | Non-voting shares |
    | RS | Restricted shares |
    | RTS | Rights |
    | RVS | Restricted voting shares |
    | SVS | Subordinate voting shares |
    | WTS | Warrants |

    <figure>

    ![](figures/3)

    <!-- FigureContent=". RECYCLED Paper FSC FSC® C128286" -->

    </figure>


    <!-- PageFooter="3C8MZK CWPC" -->

    <!-- PageNumber="H8O3 E" -->

    <!-- PageNumber="2 of 7" -->

    """
    sample_non_disclaimer_text = r"""<figure>

![](figures/0)

<!-- FigureContent="HARBOURFRONT WEALTH MANAGEMENT" -->

</figure>


Harbourfront Wealth Management Inc. Royal Centre, Suite 1800-1055 West Georgia Street PO Box 11118 Vancouver, BC V6E 3P3

<!-- PageHeader="Investment Portfolio Statement As of August 31, 2022" -->

BLAIR STUART MCREYNOLDS 61 SOVEREIGN DR ST CATHARINES ON L2T 1Z6

Portfolio Summary

| Last Period: This Period: July 31, 2022 August 31, 2022 ||||||
| Account Type | Total Cash & Investments ($) | Cash ($) | Investments ($) | Total Cash & Investments ($) | % |
| - | - | - | - | - | - |
| CAD Cash | 34,197.29 | 4,755.93 | 28,688.80 | 33,444.73 | 9.7 |
| CAD RRSP | 281,940.94 | 9,249.72 | 239,282.43 | 248,532.15 | 72.3 |
| CAD LRSP | 10,713.37 | 599.24 | 8,796.80 | 9,396.04 | 2.7 |
| CAD TFSA | 53,406.53 | 15,007.39 | 37,410.20 | 52,417.59 | 15.3 |
| Total | 380,258.13 | 29,612.28 | 314,178.23 | 343,790.51 | 100.0 |

Portfolio Asset Allocation

| | Market Value ($) | % |
| - | - | - |
| Cash and Equivalents | 29,612.28 | 8.6 |
| Equities and Equity Funds | 84,964.38 | 24.7 |
| Other Assets | 229,213.85 | 66.7 |
| Total | 343,790.51 | 100.0 |

Portfolio Statement Information

Client ID #

3C8MZK

Contact Information

Your Investment Advisor: RICHARDSON & ASSOCIATES 705-797-4950 Bill Richardson CIM, CFP BRichardson@harbourfrontwealth.com 479 King Street Midland, ON L4R 3N4 \*Foreign Exchange Rates

Portfolio Summary and Portfolio Asset Allocation amounts are stated in Canadian dollars, according to the month-end conversion rate. USD 1.00 = CAD 1.309415 CAD 1.00 = USD 0.763700

Inside This Statement

|||
| - | - |
| CAD Cash | 3 |
| CAD RRSP | 4 |
| CAD LRSP | 5 |
| CAD TFSA | 6 |

CIPF Canadian Investor Protection Fund MEMBER

<figure>

![](figures/1)

<!-- FigureContent="IIROC" -->

</figure>


<!-- PageNumber="Regulated by Investment Industry Regulatory Organization of Canada 3C8MZK CWPC H8O3 E 1 of 7" -->
<figure>

![](figures/2)

<!-- FigureContent="HARBOURFRONT WEALTH MANAGEMENT" -->

</figure>


Investment Portfolio Statement As of August 31, 2022"""
    sample_generic_statement_exerpt = r"""The amounts shown in this section are given in Canadian dollars.
    The subsection on Asset Allocation indicates how the consolidated financial assets you hold with us are distributed across each of the basic asset classes. Any securities sold short or debit cash positions are excluded from this asset mix calculation."""
    sample_non_generic_statement_exerpt = r"""| - | - |
    | Your Account Number: | 374-40273-1-3 |
    | Trustee: | Royal Trust Company |
    | Date of Last Statement: | FEB. 28, 2023 |"""

    import time

    start_time = time.time()
    # result = classifier.classify(
    #     sample_disclaimer_text, "meta-llama-3.1-8b-instruct-q4_k_m"
    # )
    # print(result, "DISCLAIMER")
    # result = classifier.classify(
    #     sample_non_disclaimer_text, "meta-llama-3.1-8b-instruct-q4_k_m"
    # )
    # print(result, "NON-DISCLAIMER")

    # classifier = StatementExerptClassifier(provider="local-lm-studio")
    classifier = StatementExerptClassifier(provider="azure-openai")
    result = classifier.classify(sample_generic_statement_exerpt, "gpt-4o-mini")
    print(result, "GENERIC")
    classifier = StatementExerptClassifier(provider="local-lm-studio")
    result = classifier.classify(
        sample_non_generic_statement_exerpt, "meta-llama-3.1-8b-instruct-q4_k_m"
    )
    print(result, "NON-GENERIC")

    end_time = time.time()
    print(f"Time taken: {end_time - start_time} seconds")
