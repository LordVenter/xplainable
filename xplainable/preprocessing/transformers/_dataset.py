from ...utils import xwidgets as xwidgets
from ._base import XBaseTransformer

import pandas.api.types as pdtypes
import pandas as pd
from ipywidgets import interactive
import ipywidgets as widgets
import numpy as np
import scipy.signal as ss
from IPython.display import display


class DropCols(XBaseTransformer):
    """Drops specified columns from a dataset.

    Args:
        columns (str): The columns to be dropped.
    """

    supported_types = ['dataset']

    def __init__(self, columns=None):
        super().__init__()
        self.columns = columns

    def __call__(self, df, *args, **kwargs):
        
        def _set_params(columns=xwidgets.SelectMultiple(options=df.columns)):

            self.columns = list(columns)

        return interactive(_set_params)

    def _operations(self, df):
        
        df = df.copy()

        # Apply column dropping
        for c in self.columns:
            if c in df.columns:
                df = df.drop(columns=[c])

        return df

class DropNaNs(XBaseTransformer):
    """Drops nan rows from a dataset.

    Args:
        subset (list, optional): A subset of columns to apply the transfomer.
    """

    supported_types = ['dataset']

    def __init__(self, subset=None):
        super().__init__()
        self.subset = subset

    def __call__(self, df, *args, **kwargs):
        
        def _set_params(
            subset=xwidgets.SelectMultiple(options=[None]+list(df.columns))):

            self.subset = list(subset)

        return interactive(_set_params)

    def _operations(self, df):

        subset = list(df.columns) if self.subset is None else self.subset
        subset = [i for i in subset if i in df.columns]

        return df.copy().dropna(subset=subset)

class Operation(XBaseTransformer):
    """Applies operation to multiple columns (in order) into new feature.

    Args:
        columns (list): Column names to add.
        alias (str): Name of newly created column.
        drop (bool): Drops original columns if True
    """
    
    # Attributes for ipyxwidgets
    supported_types = ['dataset']

    def __init__(self, columns=[], operation=None, alias: str = None, drop: bool = False):
        super().__init__()
        self.columns = columns
        self.operation = operation
        self.alias = alias if alias else " + ".join([c for c in columns])
        self.drop = drop

    def __call__(self, dataset, *args, **kwargs):
        
        cols = list(dataset.columns)
        
        def _set_params(
            columns_to_apply=xwidgets.SelectMultiple(
                description='Columns: ',
                value=[cols[0]],
                options=cols,
                allow_duplicates=False),
            tags = xwidgets.TagsInput(
                value=[cols[0]],
                allowed_tags=cols
            ),
            operation=['add', 'multiply', 'average', 'concatenate'],
            alias=xwidgets.Text(''),
            drop_columns=xwidgets.Checkbox(value=True)):

            self.columns = list(columns_to_apply)
            self.operation = operation
            self.alias = alias
            self.drop = drop_columns
        
        widget = interactive(_set_params)
        dd = widget.children[0]
        tags = widget.children[1]
        
        widget.children[3].layout = widgets.Layout(margin='10px 0 20px 0')
        widgets.link((dd, 'value'), (tags, 'value'))
        label = widgets.HTML('Drag to reorder')
        label.layout = widgets.layout = widgets.Layout(margin='10px 0 0 0')

        tags_display = widgets.VBox([dd, label, tags])
        tags_display.layout = widgets.Layout(
            margin='0 0 0 30px',
            width='280px'
            )
        widget.children = (tags_display,) + widget.children[2:]
        
        return widget

    def _operations(self, df):

        df = df.copy()

        if self.operation == 'add':
            if not all([pdtypes.is_numeric_dtype(df[col]) for col in self.columns]):
                raise TypeError("Cannot add string and numeric columns")
            df[self.alias] = df[self.columns].sum(axis=1)

        elif self.operation == 'multiply':
            if not all([pdtypes.is_numeric_dtype(df[col]) for col in self.columns]):
                raise TypeError("Cannot add string and numeric columns")
            df[self.alias] = df[self.columns].apply(np.prod, axis=1)

        elif self.operation == 'average':
            if not all([pdtypes.is_numeric_dtype(df[col]) for col in self.columns]):
                raise TypeError("Cannot add string and numeric columns")
            df[self.alias] = df[self.columns].mean(axis=1)

        elif self.operation == 'concatenate':
            for col in self.columns:
                if not pdtypes.is_string_dtype(df[col]):
                    df[col] = df[col].astype(str)
            df[self.alias] = df[self.columns].agg('-'.join, axis=1)

        if self.drop:
            df = df.drop(columns=self.columns)

        return df


class TextTrimMulti(XBaseTransformer):
    """ Drops or keeps first/last n characters of a categorical column.

    Args:
        selector (str): [first, last].
        n (int): Number of characters to identify.
        action (str): [keep, drop] the identified characters.
    """

    # Attributes for ipywidgets
    supported_types = ['dataset']

    def __init__(
        self, column='', selector=None, n=0,
        action='keep', drop_col=False, alias=''):
        
        self.column = column
        self.selector = selector
        self.n = n
        self.action = action
        self.drop_col = drop_col
        self.alias = alias

    def __call__(self, dataset, *args, **kwargs):

        cols = list(dataset.columns)
        
        def _set_params(
            column=xwidgets.Dropdown(
                description='Column: ',
                value=cols[0],
                options=cols),
            selector = widgets.Dropdown(options=["first", "last"]),
            n = widgets.IntText(n=1),
            action = widgets.Dropdown(options=['keep', 'drop']),
            alias = widgets.Text(''),
            drop_col = widgets.Checkbox(description="drop original")
        ):
            self.selector = selector
            self.n = n
            self.action = action
            self.alias = alias
            self.drop_col = drop_col
            self.column = column

        return interactive(_set_params)

    def _operations(self, df):
        df = df.copy()
        ser = df[self.column]

        if self.action == 'keep':
            if self.selector == "first":
                df[self.alias] = ser.str[:self.n]

            else:
                df[self.alias] = ser.str[-self.n:]
        else:
            if self.selector == "first":
                df[self.alias] = ser.str[self.n:]

            else:
                df[self.alias] = ser.str[:-self.n]

        if self.drop_col:
            df = df.drop(columns=[self.column])

        return df


class ChangeNames(XBaseTransformer):
    """Changes names of columns in a dataset"""

    # Attributes for ipyxwidgets
    supported_types = ['dataset']

    def __init__(self, col_names={}):
        super().__init__()
        self.col_names = col_names

    def __call__(self, df, *args, **kwargs):
      
        def _set_params(*args, **kwargs):
            args = locals()
            self.col_names = dict(args)['kwargs']
        
        col_names = {col: xwidgets.Text(col) for col in df.columns}
        
        w = interactive(_set_params, **col_names)
        
        for c in w.children[:-1]:
            c.description = ''
        
        return w

    def _operations(self, df):
        df = df.copy()
        col_names = {i: v for i, v in self.col_names.items() if i in df.columns}
        return df.rename(columns=col_names)


class OrderBy(XBaseTransformer):
    """ Orders the dataset by the values of a given series.

    Args:
        order_by (str): The series to order by.
        ascending (bool): Orders in ascending order if True.
    """

    # Attributes for ipyxwidgets
    supported_types = ['dataset']

    def __init__(self, order_by=None, ascending=True):
        super().__init__()
        self.order_by = order_by
        self.ascending = ascending

    def __call__(self, df, *args, **kwargs):
      
        def _set_params(
            order_by = xwidgets.SelectMultiple(
                description='Order by: ', options=[None]+list(df.columns)),
            direction = xwidgets.ToggleButtons(
                description='Direction: ',
                options=['ascending', 'descending'])):

            self.order_by = list(order_by)
            self.ascending = True if direction == 'ascending' else False

        return interactive(_set_params)

    def _operations(self, df):

        return df.sort_values(self.order_by, ascending=self.ascending)


class GroupbyShift(XBaseTransformer):
    """ Shifts a series up or down n steps within specified group.

    Args:
        target (str): The target feature to shift.
        step (int): The number of steps to shift.
        as_new (bool): Creates new column if True.
        group_by (str): The column to group by.
        order_by (str): The column to order by.
        descending (bool): Orders the value descending if True.
    """

    # Attributes for ipyxwidgets
    supported_types = ['dataset']

    def __init__(self, columns=None, step=0, as_new=True, col_names=[], \
        group_by=None, order_by=None, descending=None):

        super().__init__()
        self.columns = columns
        self.step = step
        self.as_new = as_new
        self.col_names = col_names

        self.group_by = group_by
        self.order_by = order_by
        self.descending = descending

    def __call__(self, df, *args, **kwargs):
        
        def _set_params(
            group_by = xwidgets.SelectMultiple(
                description='Group by: ', options=[None]+list(df.columns)),
            order_by = xwidgets.SelectMultiple(
                description='Order by: ', options=[None]+list(df.columns)),
            descending = xwidgets.Checkbox(value=False),
            columns=xwidgets.SelectMultiple(
                description='Columns: ', options=[None]+list(df.columns)),
            step = xwidgets.IntText(value=0, min=-1000, max=1000),
            as_new = xwidgets.Checkbox(value=False)
            ):

            self.columns = columns
            self.group_by = list(group_by)
            self.order_by = list(order_by)
            self.descending = descending
            self.step = step

            self.as_new = as_new

            # build new col names if as_new
            if as_new and len(columns) > 0:
                for target in columns:
                    col_name = f'{target}_shift_{step}'
                    if len(self.group_by) > 0:
                        col_name += "_gb_"
                        col_name += '_'.join(self.group_by)

                    if len(self.order_by) > 0:
                        col_name += "_ob_"
                        col_name += '_'.join(self.order_by)
                
                    self.col_names.append(col_name)

        return interactive(_set_params)

    def _operations(self, df):

        # Order values if
        if self.order_by and self.order_by[0] is not None:
            df = df.sort_values(self.order_by, ascending=not self.descending)

        for col_name, target in zip(self.col_names, self.columns):
            if self.group_by and self.group_by[0] is not None:
                df[col_name] = df.groupby(
                    self.group_by)[target].shift(self.step)
            else:
                df[col_name] = df[target].shift(self.step)

        return df


class FillMissing(XBaseTransformer):
    """Fills missing values of all columns with a specified value/strategy."""

    # Attributes for ipyxwidgets
    supported_types = ['dataset']

    def __init__(self, fill_with={}, fill_values={}):
        super().__init__()
        self.fill_with = fill_with
        self.fill_values = fill_values

    def __call__(self, df, *args, **kwargs):
      
        def _set_params(*args, **kwargs):
            args = locals()
            self.fill_with = dict(args)['kwargs']

        def get_widget(col):
            if pdtypes.is_numeric_dtype(df[col]):
                return xwidgets.Dropdown(options=["mean", "median", "mode"])
            else:
                return xwidgets.Text(value='missing')

        col_xwidgets = {col: get_widget(col) for col in df.columns}  

        return interactive(_set_params, **col_xwidgets)

    def _operations(self, df):
        
        for i, v in self.fill_values.items():
            if i not in df.columns:
                continue
            df[i] = df[i].fillna(v)

        return df

    def fit(self, df):
        """ Calculates the fill_value from a given series.

        Args:
            ser (pandas.Series): The series in which to analyse.

        Returns:
            self
        """

        for i, v in self.fill_with.items():
            # Calculate fill_value if mean, median or mode
            if v == 'mean':
                self.fill_values[i] = round(np.nanmean(df[i]), 4)

            elif v == 'median':
                self.fill_values[i] = np.nanmedian(df[i])

            elif v == 'mode':
                self.fill_values[i] = df[i].mode()

            else:
                self.fill_values[i] = v

            # Maintain fill value type (if int)
            if pdtypes.is_integer_dtype(df[i]):
                self.fill_values[i] = int(self.fill_values[i])

        return self


class SetDTypes(XBaseTransformer):
    """Sets the data type of all columns in the dataset."""

    # Attributes for ipyxwidgets
    supported_types = ['dataset']

    def __init__(self, types={}):
        super().__init__()
        self.types = types

    def __call__(self, df, *args, **kwargs):
      
        def _set_params(*args, **kwargs):
            args = locals()
            self.types = dict(args)['kwargs']

        def get_widget(col):
            if pdtypes.is_float_dtype(df[col]):
                options=["float", "integer", "string"]
                value = 'float'

            elif pdtypes.is_integer_dtype(df[col]):
                options=["float", "integer", "string"]
                value = 'integer'

            elif pdtypes.is_string_dtype(df[col]):
                #options=["string"]
                options=["float", "integer", "string"]
                # if all(df[col].str.isdigit()):
                #     options += ["float", "integer"]
                value = 'string'
            
            elif pdtypes.is_datetime64_dtype(df[col]):
                options = ["date", "string"]
                value = "date"

            elif pdtypes.is_bool_dtype(df[col]):
                options = ["boolean", "string", "integer", "float"]
                value = "boolean"

            w = xwidgets.Dropdown(
                options=options,
                value=value,
                style={'description_width': 'initial'}
                )

            return w

        col_xwidgets = {col: get_widget(col) for col in df.columns}  

        return interactive(_set_params, **col_xwidgets)

    def _operations(self, df):

        for i, v in self.types.items():
            
            if i not in df.columns:
                continue

            if v == 'string':
                df[i] = df[i].astype(str)
                continue
            
            df[i] = pd.to_numeric(df[i], errors='coerce')

            if v == 'integer':
                # If missing value are present, cannot cast to int
                try:
                    df[i] = df[i].astype(int)
                except Exception:
                    continue

        return df


class TextSplit(XBaseTransformer):
    """ Splits a string column into multiple columns on a specified separator.

    Args:
        target (str): The columns to split.
        separator (str): The separator to split on.
        max_splits (int): The maximum number of splits to make.
    """

    # Attributes for ipyxwidgets
    supported_types = ['dataset']

    def __init__(self, target=None, separator=None, max_splits=0):

        self.target = target
        self.separator = separator
        self.max_splits = max_splits

    def __call__(self, df, *args, **kwargs):
        
        def _set_params(
            target=xwidgets.Dropdown(
                options=[None]+[i for i in df.columns if \
                    pdtypes.is_string_dtype(df[i])]),
                separator = xwidgets.Text(value=""),
                max_splits = xwidgets.IntText(range=[0,10])):

            self.target = target
            self.separator = separator
            self.max_splits = max([max_splits, 0])

        return interactive(_set_params)

    def _operations(self, df):

        new_cols = df[self.target].astype(str).str.split(
            self.separator, expand=True, n=self.max_splits)
        new_cols.columns = [f'{self.target}_{i}' for i in new_cols]
        df[new_cols.columns] = new_cols
        df = df.drop(columns=[self.target])

        return df


class ChangeCases(XBaseTransformer):
    """ Changes the case of all specified categorical columns.

    Args:
        columns (list): The to apply the case change.
        case (str): 'upper' or 'lower'.
    """

    # Attributes for ipyxwidgets
    supported_types = ['dataset']

    def __init__(self, columns=[], case='lower'):
        super().__init__()
        self.columns = columns
        self.case = case

    def __call__(self, df, *args, **kwargs):
        
        def _set_params(
            columns = xwidgets.SelectMultiple(
                description='Columns: ',
                options=[None]+[i for i in df.columns if \
                    pdtypes.is_string_dtype(df[i])]),

            case = xwidgets.Dropdown(
                description='Case: ',
                options=["lower", "upper"])):
            
            self.columns = list(columns)
            self.case = case
        
        return interactive(_set_params)

    def _operations(self, df):

        for col in self.columns:
            if col not in df.columns:
                continue

            if self.case == 'lower':
                df[col] = df[col].str.lower()

            elif self.case == 'upper':
                df[col] = df[col].str.upper()

            else:
                raise ValueError("case change must be either 'lower' or 'upper'")

        return df


class GroupedSignalSmoothing(XBaseTransformer):
    """ Smooths signal data within specified group.

    Args:
        target (str): The target feature to shift.
        as_new (bool): Creates new column if True.
        group_by (str): The column to group by.
        order_by (str): The column to order by.
        descending (bool): Orders the value descending if True.
    """

    # Attributes for ipyxwidgets
    supported_types = ['dataset']

    def __init__(self, target=None, group_by=None,\
        order_by=None, descending=None):

        super().__init__()
        self.target = target

        self.group_by = group_by
        self.order_by = order_by
        self.descending = descending

    def __call__(self, df, *args, **kwargs):
        
        def _set_params(
            group_by = xwidgets.SelectMultiple(
                description='Group by: ', options=[None]+list(df.columns)),
            order_by = xwidgets.SelectMultiple(
                description='Order by: ', options=[None]+list(df.columns)),
            descending = xwidgets.Checkbox(value=False),
            targets=xwidgets.SelectMultiple(options=[None]+list(df.columns))
            ):

            self.targets = targets
            self.group_by = list(group_by)
            self.order_by = list(order_by)
            self.descending = descending

        return interactive(_set_params)

    def _operations(self, df):

        # Order values if
        if self.order_by and self.order_by[0] is not None:
            df = df.sort_values(self.order_by, ascending=not self.descending)

        if self.group_by and self.group_by[0] is not None:
            for t in self.targets:
                df[t] = df.groupby(self.group_by)[t].transform(
                    lambda x: ss.savgol_filter(x, window_length=19, \
                        polyorder=1, deriv=0, mode='interp'))
        else:
            df[t] = ss.savgol_filter(
                df[t], window_length=19, polyorder=1, deriv=0, mode='interp')

        return df


class DateTimeExtract(XBaseTransformer):
    """ Extracts Datetime values from datetime object. """

    # Attributes for ipywidgets
    supported_types = ['dataset']

    def __init__(self, target=None, year=False, month=False, day=False, \
        weekday=False, day_name=False, hour=False, minute=False, \
            second=False, drop=False):

        self.target = target
        self.year = year
        self.month = month
        self.day = day
        self.weekday = weekday
        self.day_name = day_name
        self.hour = hour
        self.minute = minute
        self.second = second
        self.drop = drop


    def __call__(self, df, *args, **kwargs):
        
        def _set_params(
            target=widgets.Dropdown(options=df.columns),
            year=widgets.ToggleButton(value=False),
            month=widgets.ToggleButton(value=False),
            day=widgets.ToggleButton(value=False),
            weekday=widgets.ToggleButton(value=False),
            day_name=widgets.ToggleButton(value=False),
            hour=widgets.ToggleButton(value=False),
            minute=widgets.ToggleButton(value=False),
            second=widgets.ToggleButton(value=False),
            drop = widgets.Checkbox(value=False)
        ):

            self.target = target
            self.year = year
            self.month = month
            self.day = day
            self.weekday = weekday
            self.day_name = day_name
            self.hour = hour
            self.minute = minute
            self.second = second
            self.drop = drop

        w = interactive(_set_params)
        _target = w.children[0]
        left = widgets.VBox(w.children[1:5])
        right = widgets.VBox(w.children[5:9])
        buttons = widgets.HBox([left, right])
        _drop = w.children[9]
        elements = widgets.VBox([_target, buttons, _drop])
                
        return elements

    def _operations(self, df):

        df = df.copy()

        try:
            df[self.target] = pd.to_datetime(df[self.target])
        except:
            raise TypeError(f"{self.target} can not be coerced to datetime")

        if self.year:
            df[f'{self.target}_year'] = df[self.target].dt.year
        
        if self.month:
            df[f'{self.target}_month'] = df[self.target].dt.month

        if self.day:
            df[f'{self.target}_day'] = df[self.target].dt.day

        if self.weekday:
            df[f'{self.target}_weekday'] = df[self.target].dt.weekday

        if self.day_name:
            df[f'{self.target}_day_name'] = df[self.target].dt.day_name()

        if self.hour:
            df[f'{self.target}_hour'] = df[self.target].dt.hour

        if self.minute:
            df[f'{self.target}_minute'] = df[self.target].dt.minute

        if self.second:
            df[f'{self.target}_second'] = df[self.target].dt.second

        if self.drop:
            df = df.drop(columns=[self.target])

        return df


class RollingOperation(XBaseTransformer):
    """Applies operation to multiple columns (in order) into new feature.

    Args:
        columns (list): Column names to add.
        alias (str): Name of newly created column.
        drop (bool): Drops original columns if True
    """
    
    # Attributes for ipyxwidgets
    supported_types = ['dataset']

    def __init__(
        self,
        groupby=None,
        orderby=None,
        direction=None,
        columns=[],
        window=None,
        operation=None,
        drop: bool = False
        ):

        super().__init__()
        self.groupby = groupby
        self.orderby = orderby
        self.direction = direction
        self.columns = columns
        self.window = window
        self.operation = operation
        self.drop = drop

    def __call__(self, df, *args, **kwargs):
        
        cols = list(df.columns)
        
        def _set_params(
            group_by = xwidgets.SelectMultiple(
                description='Group by: ', options=[None]+list(df.columns)),
            order_by = xwidgets.SelectMultiple(
                description='Order by: ', options=[None]+list(df.columns)),
            direction = xwidgets.ToggleButtons(
                description='Direction: ',
                options=['ascending', 'descending']),
            columns_to_apply=xwidgets.SelectMultiple(
                description='Columns: ',
                value=[cols[0]],
                options=cols,
                allow_duplicates=False),
            window=xwidgets.IntText(min=2, value=3),
            operation=['mean', 'sum', 'max', 'min'],
            drop_columns=xwidgets.Checkbox(value=True)):

            self.groupby = list(group_by)
            self.orderby = list(order_by)
            self.direction = direction
            self.columns = list(columns_to_apply)
            self.operation = operation
            self.window = window
            self.drop = drop_columns
        
        widget = widgets.interactive(_set_params)

        widget.children[6].layout = widgets.Layout(margin='10px 0 20px 0')

        widget.layout = widgets.Layout(
            margin='0 0 0 30px',
            width='280px'
            )

        return widget

    def _operations(self, df):

        df = df.copy()

        assert all(
            [pdtypes.is_numeric_dtype(df[col]) for col in self.columns]
            ), "Selected columns must be numeric"

        asc = True if self.direction == 'ascending' else False

        for col in self.columns:
            alias = f'{col}_{self.operation}_{self.window}'

            if self.operation == 'mean':
                if self.groupby:
                    df[alias] = df.sort_values(
                        self.orderby, ascending=asc).groupby(self.groupby).rolling(
                            self.window).mean()[col].values
                else:
                    df[alias] = df[col].rolling(self.window).mean()

            elif self.operation == 'sum':
                if self.groupby:
                    df[alias] = df.sort_values(
                        self.orderby, ascending=asc).groupby(self.groupby).rolling(
                            self.window).sum()[col].values
                else:
                    df[alias] = df[col].rolling(self.window).sum()

            elif self.operation == 'max':
                if self.groupby:
                    df[alias] = df.sort_values(
                        self.orderby, ascending=asc).groupby(self.groupby).rolling(
                            self.window).max()[col].values
                else:
                    df[alias] = df[col].rolling(self.window).max()

            elif self.operation == 'min':
                if self.groupby:
                    df[alias] = df.sort_values(
                        self.orderby, ascending=asc).groupby(self.groupby).rolling(
                            self.window).min()[col].values
                else:
                    df[alias] = df[col].rolling(self.window).min()

            if self.drop:
                df = df.drop(columns=self.columns)

        return df