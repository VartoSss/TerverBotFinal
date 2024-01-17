import os
import pandas as pd


class CSVParser:

    @staticmethod
    def parse(filepath: str) -> list[list[str]]:
        df = pd.read_csv(filepath, delimiter=';')
        result = []
        values = df.values.tolist()
        for value in values:
            result.append([str(item) for item in value])
        return result
