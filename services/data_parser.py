from pandas import DataFrame

class DataParser:
    def __init__(self, file_path: str, separator=';'):
        self.file_path = file_path
        self.separator = separator

    def parse(self) -> DataFrame:
        file_text = self.__read_file()
        prepared_rows = self.__prepare_rows(file_text)

        headers = prepared_rows[0].strip('% ').split(self.separator)
        data = self.__prepare_data(prepared_rows[1:])
        return DataFrame(data, columns=headers)

    def __read_file(self) -> list[str]:
        with open(self.file_path, 'r') as f:
            return f.readlines()[8:]

    def __prepare_data(self, data: list[str]) -> list[list[float]]:
        prepared_data = []
        split_data = map(lambda s: s.split(self.separator), data)

        for row in split_data:
            prepared_data.append(list(map(lambda s: float(s), row)))
        return prepared_data


    @staticmethod
    def __prepare_rows(rows: list[str]) -> list[str]:
        prepared_rows = []
        for row in rows:
            prepared_rows.append(row.strip())
        return prepared_rows


if __name__ == '__main__':
    parser = DataParser('../data/semicolon.txt')
    data = parser.parse()
    c=1