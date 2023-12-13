from _datetime import datetime, timedelta


class Client:
    def __init__(self, title: str, link: str, description: str, category: str, budget: str, posted_on: str,
                 country: str, valid_budget: float):
        self.title = title
        self.link = link
        self.description = description
        self.category = category
        self.budget = self.try_convert_float(budget, valid_budget)
        self.job_post_time = datetime.strptime(posted_on, "%B %d, %Y %H:%M %Z") + timedelta(hours=5)
        self.country = country

    def get_message(self):
        message = ''
        message += self.title + '\n(' + self.link + ')\n'
        message += 'Description : \n'
        message += self.description
        return message

    def try_convert_float(self, value: str, valid_budget: float) -> float:
        try:
            return 50 if len(value) == 0 else float(value.replace('$', '').replace(',', ''))
        except ValueError:
            return valid_budget

    def __str__(self):
        print(
            '=====================================================================================================================================================')
        print(self.title, '\n(', self.link, ')')
        print('Description : ')
        print(self.description)
        print(
            '=====================================================================================================================================================')
