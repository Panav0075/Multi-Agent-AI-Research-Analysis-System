import pytest
from src.tools.calculator import CalculatorTool


def test_calculator_handles_arithmetic():
    tool = CalculatorTool()
    assert tool.calculate("(12 * 4) + 2") == 50


def test_calculator_rejects_function_calls():
    tool = CalculatorTool()
    with pytest.raises(ValueError):
        tool.calculate("__import__('os').system('echo unsafe')")
