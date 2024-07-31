from azure.ai.documentintelligence.models import AnalyzeResult


def get_context(layout_analysis: AnalyzeResult) -> str:
    return layout_analysis.content
