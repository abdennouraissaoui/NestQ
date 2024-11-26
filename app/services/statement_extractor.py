"""
Orchestrates the extraction of holdings from a financial statement.
"""
from app.services.prompts import INVESTMENT_STATEMENT_DATA_EXTRACTION
from app.models.schemas.extraction_schema import ScanExtractedDataSchema
from app.services.llm_factory import LlmFactory
from app.services.ocr_service import OcrFactory
from app.services.text_cleanup import (
    remove_disclaimer_pages,
    remove_informational_text,
)
from app.utils.utility import clean_markdown_text
from typing import Tuple
from app.models.schemas.scan_schema import ScanProcessorUpdateSchema
from app.models.enums import ScanStatus
import time


class FinancialStatementProcessor:
    def __init__(
        self,
        ocr_provider: str = "document-intelligence",
        llm_provider: str = "azure-openai",
    ):
        self.ocr_factory = OcrFactory(ocr_provider)
        self.llm_factory = LlmFactory(llm_provider)

    def process_scan(
        self, file_base64: str
    ) -> Tuple[ScanProcessorUpdateSchema, ScanExtractedDataSchema]:
        start_time = time.time()
        try:
            cleaned_doc_base64 = remove_disclaimer_pages(file_base64)
        except Exception as e:
            cleaned_doc_base64 = file_base64
            print(e)

        ocr_result = self.ocr_factory.get_document_analysis(cleaned_doc_base64)

        markdown_text = clean_markdown_text(ocr_result.content)
        # context: str = "\n\n".join(self.classifier.filter_included(markdown_text.split("\n\n")))
        context: str = remove_informational_text(markdown_text)
        # context = markdown_text
        # Extract statement information only once

        extracted_data: ScanExtractedDataSchema = self.extract_financial_statement(
            context
        )

        scan_update = ScanProcessorUpdateSchema(
            statement_date=extracted_data.statement_date,
            ocr_text=markdown_text,
            ocr_text_cleaned=context,
            processing_time=float(time.time() - start_time),
            status=ScanStatus.PROCESSED,
            page_count=len(ocr_result.pages),
            ocr_source=self.ocr_factory.provider,
            llm_source=self.llm_factory.provider,
        )

        return scan_update, extracted_data

    def extract_financial_statement(
        self, context: str, model="gpt-4o"
    ) -> ScanExtractedDataSchema:
        messages = [
            {
                "role": "system",
                "content": INVESTMENT_STATEMENT_DATA_EXTRACTION["system"],
            },
            {
                "role": "user",
                "content": INVESTMENT_STATEMENT_DATA_EXTRACTION["user"].format(
                    statement_text=context
                ),
            },
        ]

        completion = self.llm_factory.create_completion(
            model=model,
            response_format=ScanExtractedDataSchema,
            messages=messages,
        )

        return completion.choices[0].message.parsed


# Example usage

if __name__ == "__main__":
    extractor = FinancialStatementProcessor(llm_provider="azure-openai")
    context = """'Monthly Account Statement As at August 30, 2024\n===\n\n\nAISSAOUI ABDENNOUR 75 HAVENBROOK BOULEVARD NORTH YORK TORONTO ONTARIO M2J1A8\n\nAll monetary values are displayed in CAD unless specified otherwise. Exchange Rate at 2024/08/30: 1.00 USD = 1.348163 CAD\n\n\n| || % |\n| - | - | - |\n| US Equity || 44.3% |\n| :selected: | Large Cap | 32.4% |\n| :unselected: | Mid Cap | 11.9% |\n| | Canadian Equity | 40.7% |\n| :selected: | Composite | 30.6% |\n| :unselected: | Low Volatility | 5.2% |\n| :unselected: | Small Cap | 5.0% |\n| | Intl Equity | 14.3% |\n| :unselected: | Emerging Markets | 9.5% |\n| :unselected: | Developed Markets | 4.8% |\n| | Cash & Equivalent | 0.7% |\n| :selected: | Cash Balance | 0.7% |\n| | | 100 % |\n\n\n# Performance (ROR) as of August 30, 2024\n\n| Portfolio: PMJW0001-182626 |||||||\n| Period | 1 Month | 3 Months | Year-to-Date | 1 Year | 3 Years | Inception |\n| - | - | - | - | - | - | - |\n| Beginning date | 2024/07/31 | 2024/05/31 | 2023/12/29 | 2023/08/31 | 2021/08/31 | 2021/03/31 |\n| Beginning Market Value | 109,923 | 104,248 | 88,337 | 80,855 | 13,167 | 0 |\n| Inflows | 500 | 1,500 | 9,000 | 12,750 | 80,150 | 92,870 |\n| Outflows | 0 | 0 | 0 | 0 | 0 | 0 |\n| Ending Market Value | 110,601 | 110,601 | 110,601 | 110,601 | 110,601 | 110,601 |\n| Rate of Return | 0.2% | 4.6% | 14.3% | 19.3% | 4.8% | 5.6% |\n\n| Period | 1 Month | 3 Months | Year-to-Date | 1 Year | 3 Years | Inception |\n| - | - | - | - | - | - | - |\n| iShares Core Canadian Universe Bond Index ETF (CAD) | 0.1% | 3.1% | -0.1% | 4.4% | -4.2% | -3.3% |\n| S&P/TSX Capped Composite Index | 1.0% | 4.8% | 11.4% | 15.0% | 4.3% | 6.7% |\n| S&P 500 Index | 2.3% | 7.0% | 18.4% | 25.3% | 7.7% | 10.8% |\n\n\\- The Rates of Return (ROR) for periods longer than 1 year are annualized returns, unless indicated as cumulative.\n\n<!-- PageNumber="2/4" -->\n:unselected: :unselected: :unselected:\n# Account Summary\n\n| Account ID | I.G. model | T/D cash balance | Market Value | Total Value | Accrued Interest |\n| - | - | - | - | - | - |\n| Margin (1043058021CAD) | Justwealth Global Tax-Efficient Maximum Growth | 776.43 | 109,824.72 | 110,601.15 | 0.00 |\n| | | 776.43 | 109,824.72 | 110,601.15 | 0.00 |\n\nPositions (By account)\n\n| % of Total | Position | Quantity | Last Bid Price | Market Value | Average Cost | Book Value | Total G/L ($)\\* |\n| - | - | - | - | - | - | - | - |\n| Account: Margin (1043058021CAD) || | | | | | |\n| 0.7% | Cash & Equivalent | | | 776.43 | | 776.43 | 0.00 |\n| 40.7% | Canadian Equity | | | 45,017.15 | | 40,317.14 | 5,997.11 |\n| 30.6% | ISHARES S& P/TSX CAPPED COMPO | 907 | 37.28 | 33,812.96 | 32.9182 | 29,856.78 | 5,220.33 |\n| 5.2% | INVESCO S& P/TSX COM ETF CAD UN | 178 | 32.01 | 5,697.78 | 29.43 | 5,238.54 | 492.19 |\n| 5.0% | ISHARES S& P/TSX SMALLCAP IND | 273 | 20.17 | 5,506.41 | 19.1275 | 5,221.82 | 284.59 |\n| 44.3% | US Equity | | | 49,036.29 | | 40,277.59 | 9,467.30 |\n| 29.7% | VANGUARD S& P 500 INDEX ETF | 243 | 135.11 | 32,831.73 | 108.2246 | 26,298.58 | 7,023.99 |\n| 11.9% | ISHARES SP US MID-CAP IDX UN E | 413 | 31.94 | 13,191.22 | 26.4927 | 10,941.47 | 2,467.51 |\n| 2.7% | BMO NASDAQ 100 EQUITY HEDGED TO CAD INDEX ETF | 22 | 136.97 | 3,013.34 | 138.07 | 3,037.54 | -24.20 |\n| 14.3% | Intl Equity | | | 15,771.28 | | 15,250.17 | 718.53 |\n| 9.5% | ISHARES MSCI EMERGING MKTS IMI | 371 | 28.24 | 10,477.04 | 27.0199 | 10,024.39 | 650.07 |\n| 4.8% | ISHARES CORE MSCI EAFE IMI | 163 | 32.48 | 5,294.24 | 32.06 | 5,225.78 | 68.46 |\n| 100% | Total for Account | | | 110,601.15 | | 96,621.33 | 16,182.94 |\n\n| Activity | Process Date | Description | Unit Price | Quantity | Total Amount |\n| - | - | - | - | - | - |\n| Account: Margin (1043058021CAD) ||| | | |\n| EFT | 2024/08/01 | EFT 104305802-104305802 | | | 500.00 |\n| DIV | 2024/08/08 | INVESCO S&P/TSX COM ETF CAD UN - DIV - INVESCO S&P/TSX COM ETF CAD UN | 30.72 | | 16.81 |\n| MGT | 2024/08/23 | Management Fee - July 202407 | | | -26.30 |\n\n|||\n| - | - |\n| Account: Margin (1043058021CAD) | |\n| Dividends | 16.81 |\n| on Stocks | 16.81 |\n| INVESCO S&P/TSX COM ETF CAD UN | 16.81 |\n| Total for Account | 16.81 |\n| Total for Portfolio | 16.81 |'"""
    print(context)
    # financial_statement = extractor.extract_financial_statement(
    #     context, model="gpt-4o"
    # )

    # # Optionally, you can also save this to a CSV file
    # # df.to_csv("financial_statement.csv", index=False)

    # print(financial_statement)
