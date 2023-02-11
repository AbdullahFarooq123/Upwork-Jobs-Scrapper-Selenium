from _datetime import datetime, timedelta


class Client:
    def __init__(self, title: str, link: str, description: str, category: str, budget: str, posted_on: str,
                 country: str):
        self.title = title
        self.link = link
        self.description = description
        self.category = category
        self.budget = 50 if len(budget) == 0 else float(budget.replace('$', '').replace(',', ''))
        self.job_post_time = datetime.strptime(posted_on, "%B %d, %Y %H:%M %Z") + timedelta(hours=5)
        self.country = country

    def get_message(self):
        message = ''
        message += self.title + '\n(' + self.link + ')\n'
        message += 'Description : \n'
        message += self.description
        return message

    def __str__(self):
        print(
            '=====================================================================================================================================================')
        print(self.title, '\n(', self.link, ')')
        print('Description : ')
        print(self.description)
        print(
            '=====================================================================================================================================================')
