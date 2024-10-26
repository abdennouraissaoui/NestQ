import pandas as pd
from abc import ABC, abstractmethod
from collections import Counter

KEYWORDS_DISCLAIMER_PAGE_DETECTION = [
    "disclaimer",
    "information",
    "tax",
    "sales",
    "deferred",
    "charge",
]

# TODO: Add keywords that are in other pages but not in disclaimer pages.

KEYWORDS_NON_DISCLAIMER_PAGE_DETECTION = ["quantity", "price"]


def count_total_keyword_occurrences(words: list[str], keywords: list[str]) -> int:
    return sum(word in keywords for word in words)


def count_keywords(words: list[str], keywords: list[str]) -> dict[str, int]:
    counter = Counter(word for word in words if word in keywords)
    return counter


class FeatureExtractor(ABC):
    def __init__(self):
        self.items = []
        self.words = []
        self.word_count = []

    def add(self, item):
        self.items.append(item.strip())
        words = item.split()
        self.words.append(words)
        self.word_count.append(len(words))

    def extract_document_features(self) -> pd.DataFrame:
        """
        Extracts features from all items added to the FeatureExtractor.

        Returns:
            pd.DataFrame: A DataFrame containing the extracted features.
        """
        features = []
        for index in range(len(self.items)):
            features.append(self.extract_features(index))
        return pd.DataFrame(features)

    @abstractmethod
    def extract_features(self, index: int) -> dict:
        """
        Extracts features from a single item.

        Args:
            index: The index of the item to extract features from.

        Returns:
            dict: A dictionary containing the extracted features.
        """
        pass


class ExcerptFeatureExtractor(FeatureExtractor):
    def extract_features(self, index: int) -> dict:
        """
        Extracts features from a single excerpt.

        Args:
            index: The index of the excerpt to extract features from.

        Returns:
            dict: A dictionary containing the extracted features.
        """
        # Implement excerpt-specific feature extraction here
        text = self.items[index]
        word_count = self.word_count[index]
        words = self.words[index]
        lines = text.split("\n")
        new_line_count = text.count("\n")
        pipe_line_count = sum(1 for line in lines if "|" in line)
        avg_line_length = word_count / len(lines) if lines else word_count
        digit_count = sum(char.isdigit() for char in text)
        digit_ratio_by_line = digit_count / len(lines) if lines else 0

        features = {
            "new_line_count": new_line_count,
            "pipe_line_ratio": pipe_line_count / new_line_count
            if new_line_count > 0
            else 0,
            "avg_line_length": avg_line_length,
            "digit_ratio_by_line": digit_ratio_by_line,
        }
        return features


class PageFeatureExtractor(FeatureExtractor):
    def extract_features(self, index: int) -> dict:
        """
        Extracts features from a single page.

        Args:
            index: The index of the page to extract features from.

        Returns:
            dict: A dictionary containing the extracted features.
        """
        page_text = self.items[index]
        page_word_count = self.word_count[index]
        words = self.words[index]
        special_symbols = '"()'  # Define the special symbols we want to count
        special_symbol_count = sum(
            page_text.count(symbol) for symbol in special_symbols
        )
        features = {
            "distance_from_start": index,
            "distance_from_end": len(self.items) - index,
            "page_word_count_ratio": page_word_count / sum(self.word_count),
            "disclaimer_keyword_ratio": count_total_keyword_occurrences(
                words, KEYWORDS_DISCLAIMER_PAGE_DETECTION
            )
            / page_word_count
            if page_word_count > 0
            else 0,
            "non_disclaimer_keyword_ratio": count_total_keyword_occurrences(
                words, KEYWORDS_NON_DISCLAIMER_PAGE_DETECTION
            )
            / page_word_count
            if page_word_count > 0
            else 0,
            "digit_count_ratio": sum(char.isdigit() for char in page_text)
            / page_word_count
            if page_word_count > 0
            else 0,
            "dollar_sign_ratio": page_text.count("$") / page_word_count
            if page_word_count > 0
            else 0,
            "special_symbol_ratio": special_symbol_count / page_word_count
            if page_word_count > 0
            else 0,
        }
        return features


if __name__ == "__main__":
    import time

    start_time = time.time()
    page_feature_extractor = PageFeatureExtractor()
    sample_text = """# Additional Information
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
    page_feature_extractor.add(sample_text)
    page_feature_extractor.add("This is a sample disclaimer text...")
    page_feature_extractor.add("This is a sample non-disclaimer text...")
    page_feature_extractor.add("This is a sample disclaimer text...")
    print(page_feature_extractor.extract_document_features())
    page_feature_extractor.extract_document_features().to_clipboard()
    end_time = time.time()
    print(f"Time taken: {end_time - start_time} seconds")
