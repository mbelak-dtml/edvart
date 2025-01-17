import warnings
from contextlib import redirect_stdout

import pandas as pd
import pytest

from edvart.report_sections import bivariate_analysis
from edvart.report_sections.bivariate_analysis import BivariateAnalysis
from edvart.report_sections.code_string_formatting import get_code


def get_test_df() -> pd.DataFrame:
    test_df = pd.DataFrame(data=[[1.1, "a"], [2.2, "b"], [3.3, "c"]], columns=["A", "B"])

    return test_df


def test_default_config_verbosity():
    bivariate_section = bivariate_analysis.BivariateAnalysis()
    assert bivariate_section.verbosity == 0, "Verbosity should be 0"
    for s in bivariate_section.subsections:
        assert s.verbosity == 0, "Verbosity should be 0"


def test_high_verobisities():
    with pytest.raises(ValueError):
        bivariate_analysis.BivariateAnalysis(verbosity=3)
    with pytest.raises(ValueError):
        bivariate_analysis.BivariateAnalysis(verbosity_contingency_table=3)
    with pytest.raises(ValueError):
        bivariate_analysis.BivariateAnalysis(verbosity_pairplot=5)
    with pytest.raises(ValueError):
        bivariate_analysis.BivariateAnalysis(verbosity_correlations=10)


def test_global_verbosity_overriding():
    bivariate_section = bivariate_analysis.BivariateAnalysis(
        verbosity=0, verbosity_pairplot=1, verbosity_correlations=2, verbosity_contingency_table=1
    )

    assert bivariate_section.verbosity == 0
    for subsec in bivariate_section.subsections:
        if isinstance(subsec, bivariate_analysis.PairPlot):
            assert subsec.verbosity == 1, "Verbosity of pairplot should be 1"
        elif isinstance(subsec, bivariate_analysis.CorrelationPlot):
            assert subsec.verbosity == 2, "Verbosity of correlation plot should be 2"
        elif isinstance(subsec, bivariate_analysis.ContingencyTable):
            assert subsec.verbosity == 1, "Verbosity of contingency table should be 1"
        else:
            pytest.fail("Unexpected subsection type.")


def test_verbosity_propagation():
    bivariate_section = bivariate_analysis.BivariateAnalysis(verbosity=2)
    assert bivariate_section.verbosity == 2, "Bivariate analysis global verbosity should be 2."

    for subsec in bivariate_section.subsections:
        if isinstance(subsec, bivariate_analysis.PairPlot):
            assert subsec.verbosity == 2, "PairPlot verbosity should be 2"
        elif isinstance(subsec, bivariate_analysis.ContingencyTable):
            assert subsec.verbosity == 2, "ContingencyTable verbosity should be 2."
        elif isinstance(subsec, bivariate_analysis.CorrelationPlot):
            assert subsec.verbosity == 2, "Correlation plot verbosity should be 2."
        else:
            pytest.fail("Unexpected subsection type")


def test_negative_verbosities():
    with pytest.raises(ValueError):
        bivariate_analysis.BivariateAnalysis(verbosity=-2)
    with pytest.raises(ValueError):
        bivariate_analysis.BivariateAnalysis(verbosity_correlations=-2)
    with pytest.raises(ValueError):
        bivariate_analysis.BivariateAnalysis(verbosity_pairplot=-1)
    with pytest.raises(ValueError):
        bivariate_analysis.BivariateAnalysis(verbosity_contingency_table=-3)


def test_section_adding():
    bivariate_section = bivariate_analysis.BivariateAnalysis(
        subsections=[
            bivariate_analysis.BivariateAnalysis.BivariateAnalysisSubsection.PairPlot,
            bivariate_analysis.BivariateAnalysis.BivariateAnalysisSubsection.CorrelationPlot,
            bivariate_analysis.BivariateAnalysis.BivariateAnalysisSubsection.PairPlot,
            bivariate_analysis.BivariateAnalysis.BivariateAnalysisSubsection.PairPlot,
            bivariate_analysis.BivariateAnalysis.BivariateAnalysisSubsection.ContingencyTable,
        ]
    )
    assert isinstance(
        bivariate_section.subsections[0], bivariate_analysis.PairPlot
    ), "Subsection should be Pairplot"
    assert isinstance(
        bivariate_section.subsections[1], bivariate_analysis.CorrelationPlot
    ), "Subsection should be CorrelationPlot"
    assert isinstance(
        bivariate_section.subsections[2], bivariate_analysis.PairPlot
    ), "Subsection should be Pairplot"
    assert isinstance(
        bivariate_section.subsections[3], bivariate_analysis.PairPlot
    ), "Subsection should be Pairplot"
    assert isinstance(
        bivariate_section.subsections[4], bivariate_analysis.ContingencyTable
    ), "Subsection should be ContingencyTable"


def test_code_export_verbosity_0():
    bivariate_section = bivariate_analysis.BivariateAnalysis(verbosity=0)
    # Export code
    exported_cells = []
    bivariate_section.add_cells(exported_cells)
    # Remove markdown and other cells and get code strings
    exported_code = [cell["source"] for cell in exported_cells if cell["cell_type"] == "code"]
    # Define expected code
    expected_code = ["bivariate_analysis(df=df)"]
    # Test code equivalence
    assert len(exported_code) == 1
    assert exported_code[0] == expected_code[0], "Exported code mismatch"


def test_code_export_verbosity_0_with_subsections():
    bivariate_section = bivariate_analysis.BivariateAnalysis(
        subsections=[
            bivariate_analysis.BivariateAnalysis.BivariateAnalysisSubsection.ContingencyTable,
            bivariate_analysis.BivariateAnalysis.BivariateAnalysisSubsection.PairPlot,
        ],
        verbosity=0,
    )
    # Export code
    exported_cells = []
    bivariate_section.add_cells(exported_cells)
    # Remove markdown and other cells and get code strings
    exported_code = [cell["source"] for cell in exported_cells if cell["cell_type"] == "code"]
    # Define expected code
    expected_code = [
        "bivariate_analysis(df=df, subsections=["
        "BivariateAnalysis.BivariateAnalysisSubsection.ContingencyTable, "
        "BivariateAnalysis.BivariateAnalysisSubsection.PairPlot])"
    ]
    # Test code equivalence
    assert len(exported_code) == 1
    assert exported_code[0] == expected_code[0], "Exported code mismatch"


def test_generated_code_verbosity_0_columns():
    columns = [f"col{i}" for i in range(5)]
    columns_x = [f"col_x{i}" for i in range(6)]
    columns_y = [f"col_y{i}" for i in range(4)]
    columns_pairs = [(f"first{i}", f"second{i}") for i in range(8)]
    bivariate_section = bivariate_analysis.BivariateAnalysis(
        columns=columns,
        columns_x=columns_x,
        columns_y=columns_y,
        columns_pairs=columns_pairs,
        verbosity=0,
        color_col="col3",
    )
    # Export code
    exported_cells = []
    bivariate_section.add_cells(exported_cells)
    # Remove markdown and other cells and get code strings
    exported_code = [cell["source"] for cell in exported_cells if cell["cell_type"] == "code"]
    # Define expected code
    expected_code = [
        f"bivariate_analysis(df=df, columns_x={columns_x}, "
        f"columns_y={columns_y}, columns_pairs={columns_pairs}, color_col='col3')"
    ]
    # Test code equivalence
    assert len(exported_code) == 1
    assert exported_code[0] == expected_code[0], "Exported code mismatch"


def test_generated_code_verobsity_1():
    bivariate_section = bivariate_analysis.BivariateAnalysis(
        verbosity=1,
        subsections=[
            bivariate_analysis.BivariateAnalysis.BivariateAnalysisSubsection.PairPlot,
            bivariate_analysis.BivariateAnalysis.BivariateAnalysisSubsection.CorrelationPlot,
            bivariate_analysis.BivariateAnalysis.BivariateAnalysisSubsection.ContingencyTable,
        ],
    )

    exported_cells = []
    bivariate_section.add_cells(exported_cells)
    exported_code = [cell["source"] for cell in exported_cells if cell["cell_type"] == "code"]

    expected_code = [
        "plot_pairplot(df=df)",
        "plot_correlations(df=df)",
        "contingency_tables(df=df)",
    ]

    assert len(expected_code) == len(exported_code)
    for expected_line, exported_line in zip(expected_code, exported_code):
        assert expected_line == exported_line, "Exported code mismatch"


def test_generated_code_verbosity_1_columns_x_y():
    columns_x = ["a", "b"]
    columns_y = ["c", "d"]
    bivariate_section = bivariate_analysis.BivariateAnalysis(
        verbosity=1,
        columns_x=columns_x,
        columns_y=columns_y,
        subsections=[
            bivariate_analysis.BivariateAnalysis.BivariateAnalysisSubsection.PairPlot,
            bivariate_analysis.BivariateAnalysis.BivariateAnalysisSubsection.CorrelationPlot,
            bivariate_analysis.BivariateAnalysis.BivariateAnalysisSubsection.ContingencyTable,
        ],
        color_col="b",
    )

    exported_cells = []
    bivariate_section.add_cells(exported_cells)
    exported_code = [cell["source"] for cell in exported_cells if cell["cell_type"] == "code"]

    expected_code = [
        f"plot_pairplot(df=df, columns_x={columns_x}, columns_y={columns_y}, color_col='b')",
        f"plot_correlations(df=df, columns_x={columns_x}, columns_y={columns_y})",
        f"contingency_tables(df=df, columns_x={columns_x}, columns_y={columns_y})",
    ]

    assert len(expected_code) == len(exported_code)
    for expected_line, exported_line in zip(expected_code, exported_code):
        assert expected_line == exported_line, "Exported code mismatch"


def test_generated_code_verbosity_1_columns_pairs():
    columns_pairs = [("a", "b"), ("c", "d")]
    columns_x_correct = ["a", "c"]
    columns_y_correct = ["b", "d"]
    bivariate_section = bivariate_analysis.BivariateAnalysis(
        verbosity=1,
        columns_pairs=columns_pairs,
        subsections=[
            bivariate_analysis.BivariateAnalysis.BivariateAnalysisSubsection.PairPlot,
            bivariate_analysis.BivariateAnalysis.BivariateAnalysisSubsection.CorrelationPlot,
            bivariate_analysis.BivariateAnalysis.BivariateAnalysisSubsection.ContingencyTable,
        ],
    )

    exported_cells = []
    bivariate_section.add_cells(exported_cells)
    exported_code = [cell["source"] for cell in exported_cells if cell["cell_type"] == "code"]

    expected_code = [
        f"plot_pairplot(df=df, columns_x={columns_x_correct}, columns_y={columns_y_correct})",
        f"plot_correlations(df=df, columns_x={columns_x_correct}, columns_y={columns_y_correct})",
        f"contingency_tables(df=df, columns_pairs={columns_pairs})",
    ]

    assert len(expected_code) == len(exported_code)
    for expected_line, exported_line in zip(expected_code, exported_code):
        assert expected_line == exported_line, "Exported code mismatch"


def test_generated_code_verbosity_2():
    bivariate_section = bivariate_analysis.BivariateAnalysis(
        verbosity=2,
        subsections=[
            bivariate_analysis.BivariateAnalysis.BivariateAnalysisSubsection.PairPlot,
            bivariate_analysis.BivariateAnalysis.BivariateAnalysisSubsection.CorrelationPlot,
            bivariate_analysis.BivariateAnalysis.BivariateAnalysisSubsection.ContingencyTable,
        ],
    )

    pairplot_cells = []
    bivariate_section.add_cells(pairplot_cells)
    exported_code = [cell["source"] for cell in pairplot_cells if cell["cell_type"] == "code"]

    expected_code = [
        "\n\n".join((get_code(bivariate_analysis.PairPlot.plot_pairplot), "plot_pairplot(df=df)")),
        "\n\n".join(
            (
                get_code(bivariate_analysis.CorrelationPlot.default_correlations),
                get_code(bivariate_analysis.CorrelationPlot._get_columns_x_y),
                get_code(bivariate_analysis.CorrelationPlot.plot_correlation).replace(
                    "CorrelationPlot.", ""
                ),
                get_code(bivariate_analysis.CorrelationPlot.plot_correlations).replace(
                    "CorrelationPlot.", ""
                ),
                "plot_correlations(df=df)",
            )
        ),
        "\n\n".join(
            (
                get_code(bivariate_analysis.ContingencyTable.contingency_tables).replace(
                    "ContingencyTable.", ""
                ),
                get_code(bivariate_analysis.ContingencyTable.contingency_table),
                "contingency_tables(df=df)",
            )
        ),
    ]

    assert len(expected_code) == len(exported_code)
    for expected_line, exported_line in zip(expected_code, exported_code):
        assert expected_line == exported_line, "Exported code mismatch"


def test_verbosity_0_different_subsection_verbosities():
    bivariate_section = BivariateAnalysis(
        verbosity=0,
        subsections=[
            BivariateAnalysis.BivariateAnalysisSubsection.PairPlot,
            BivariateAnalysis.BivariateAnalysisSubsection.ContingencyTable,
            BivariateAnalysis.BivariateAnalysisSubsection.PairPlot,
            BivariateAnalysis.BivariateAnalysisSubsection.CorrelationPlot,
        ],
        verbosity_pairplot=2,
        verbosity_correlations=1,
    )

    bivariate_cells = []
    bivariate_section.add_cells(bivariate_cells)
    exported_code = [cell["source"] for cell in bivariate_cells if cell["cell_type"] == "code"]

    expected_code = [
        "bivariate_analysis(df=df, "
        "subsections=[BivariateAnalysis.BivariateAnalysisSubsection.ContingencyTable])",
        get_code(bivariate_analysis.PairPlot.plot_pairplot) + "\n\n" + "plot_pairplot(df=df)",
        get_code(bivariate_analysis.PairPlot.plot_pairplot) + "\n\n" + "plot_pairplot(df=df)",
        "plot_correlations(df=df)",
    ]

    assert len(expected_code) == len(exported_code)
    for expected_line, exported_line in zip(expected_code, exported_code):
        assert expected_line == exported_line, "Exported code mismatch"


def test_imports_verbosity_0():
    bivariate_section = BivariateAnalysis(verbosity=0)

    exported_imports = bivariate_section.required_imports()
    expected_imports = [
        "from edvart.report_sections.bivariate_analysis import BivariateAnalysis\n"
        "bivariate_analysis = BivariateAnalysis.bivariate_analysis"
    ]

    assert isinstance(exported_imports, list)
    assert len(expected_imports) == len(exported_imports)
    for expected_import, exported_import in zip(expected_imports, exported_imports):
        assert expected_import == exported_import, "Exported import mismatch"


def test_imports_verbosity_1():
    bivariate_section = BivariateAnalysis(verbosity=1)

    exported_imports = bivariate_section.required_imports()
    expected_imports = list(
        set().union(*[s.required_imports() for s in bivariate_section.subsections])
    )

    assert isinstance(exported_imports, list)
    assert len(expected_imports) == len(exported_imports)
    for expected_import, exported_import in zip(expected_imports, exported_imports):
        assert expected_import == exported_import, "Exported import mismatch"


def test_imports_verbosity_2():
    bivariate_section = BivariateAnalysis(verbosity=2)

    exported_imports = bivariate_section.required_imports()
    expected_imports = list(
        set().union(*[s.required_imports() for s in bivariate_section.subsections])
    )

    assert isinstance(exported_imports, list)
    assert len(expected_imports) == len(exported_imports)
    for expected_import, exported_import in zip(expected_imports, exported_imports):
        assert expected_import == exported_import, "Exported import mismatch"


def test_imports_verbosity_0_different_subsection_verbosities():
    bivariate_section = BivariateAnalysis(
        verbosity=0,
        subsections=[
            BivariateAnalysis.BivariateAnalysisSubsection.PairPlot,
            BivariateAnalysis.BivariateAnalysisSubsection.ContingencyTable,
            BivariateAnalysis.BivariateAnalysisSubsection.PairPlot,
            BivariateAnalysis.BivariateAnalysisSubsection.CorrelationPlot,
        ],
        verbosity_pairplot=2,
        verbosity_correlations=1,
    )

    exported_imports = bivariate_section.required_imports()

    expected_imports = {
        "from edvart.report_sections.bivariate_analysis import BivariateAnalysis\n"
        "bivariate_analysis = BivariateAnalysis.bivariate_analysis"
    }
    for s in bivariate_section.subsections:
        if s.verbosity > 0:
            expected_imports.update(s.required_imports())

    assert isinstance(exported_imports, list)
    assert set(exported_imports) == set(expected_imports)


def test_show():
    bivariate_section = BivariateAnalysis()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        with redirect_stdout(None):
            bivariate_section.show(get_test_df())
