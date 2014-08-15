import numpy as np
import numpy.testing as npt
import pandas as pd
import pytest

from .. import ipu
from ...frequencytable import FrequencyTable


@pytest.fixture
def frequency_columns():
    return pd.MultiIndex.from_tuples(
        [('household', 1),
         ('household', 2),
         ('person', 1),
         ('person', 2),
         ('person', 3)])


@pytest.fixture
def frequency_table(frequency_columns):
    ft = FrequencyTable(
        index=[1, 2, 3, 4, 5, 6, 7, 8],
        household_cols={
            1: pd.Series([1, 1, 1], index=[1, 2, 3]),
            2: pd.Series([1, 1, 1, 1, 1], index=[4, 5, 6, 7, 8])
        },
        person_cols={
            1: pd.Series([1, 1, 2, 1, 1, 2, 1], index=[1, 2, 3, 4, 6, 7, 8]),
            2: pd.Series([1, 1, 2, 1, 1, 1], index=[1, 3, 5, 6, 7, 8]),
            3: pd.Series([1, 1, 2, 1, 2], index=[1, 2, 4, 5, 7])
        })

    return ft


@pytest.fixture
def constraints(frequency_columns):
    return pd.Series(
        [35, 65, 91, 65, 104], index=frequency_columns, dtype='float')


def test_fit_quality(frequency_table, constraints):
    weights = pd.Series(
        np.ones(len(frequency_table)), index=frequency_table.index)
    column = frequency_table['household'][1]
    constraint = constraints['household'][1]

    npt.assert_allclose(
        ipu.fit_quality(column, weights, constraint), 0.9143,
        atol=0.0001)

    weights = pd.Series(
        [12.37, 14.61, 8.05, 16.28, 16.91, 8.97, 13.78, 8.97],
        index=frequency_table.index)
    column = frequency_table['person'][2]
    constraint = constraints['person'][2]

    npt.assert_allclose(
        ipu.fit_quality(column, weights, constraint), 0.3222,
        atol=0.0003)


def test_average_fit_quality(frequency_table, constraints):
    weights = pd.Series(
        np.ones(len(frequency_table)), index=frequency_table.index)
    npt.assert_allclose(
        ipu.average_fit_quality(frequency_table, weights, constraints),
        0.9127,
        atol=0.0001)

    weights = pd.Series(
        [12.37, 14.61, 8.05, 16.28, 16.91, 8.97, 13.78, 8.97],
        index=frequency_table.index)
    npt.assert_allclose(
        ipu.average_fit_quality(frequency_table, weights, constraints),
        0.0954,
        atol=0.0001)


def test_update_weights(frequency_table, constraints):
    column = frequency_table['household'][1]
    constraint = constraints['household'][1]
    weights = pd.Series(
        np.ones(len(frequency_table)),
        index=frequency_table.index).loc[column.index]

    npt.assert_allclose(
        ipu.update_weights(column, weights, constraint),
        [11.67, 11.67, 11.67],
        atol=0.01)

    column = frequency_table['person'][3]
    constraint = constraints['person'][3]
    weights = pd.Series(
        [8.05, 9.51, 8.05, 10.59, 11.0, 8.97, 8.97, 8.97],
        index=frequency_table.index).loc[column.index]

    npt.assert_allclose(
        ipu.update_weights(column, weights, constraint),
        [12.37, 14.61, 16.28, 16.91, 13.78],
        atol=0.01)


def test_household_weights(frequency_table, constraints):
    weights, fit_qual, iterations = ipu.household_weights(
        frequency_table, constraints, convergence=1e-7)
    npt.assert_allclose(
        weights.as_matrix(),
        [1.36, 25.66, 7.98, 27.79, 18.45, 8.64, 1.47, 8.64],
        atol=0.02)
    npt.assert_allclose(fit_qual, 8.51e-6, atol=1e-8)
    npt.assert_allclose(iterations, 638, atol=5)