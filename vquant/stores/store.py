from pandas import DataFrame


class LocalStore(object):
    def __init__(self, columns: [str]):
        self._frame = DataFrame(columns=columns)

    def query(self, **kwargs):
        _frame = self._frame
        for key, value in kwargs.items():
            _frame = _frame.loc[_frame[key] == value]
        return _frame

    def update_or_insert(self, row: dict, **kwargs):
        _frame = self.query(**kwargs)
        updated_rows = len(_frame.index)
        if updated_rows:
            self._frame.loc[_frame.index, self._frame.columns] = list(row.values())
        else:
            self._frame = self._frame.append([row], ignore_index=True)
        return updated_rows

    def delete(self, **kwargs):
        _frame = self.query(**kwargs)
        drop_rows = len(_frame.index)
        if drop_rows:
            self._frame.drop(index=_frame.index, inplace=True)
        return drop_rows
