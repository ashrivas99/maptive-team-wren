"""Web Scraping module."""
from time import sleep
import json
from bs4 import BeautifulSoup
from selenium import webdriver

SITE_URL = "https://mathopolis.com/questions/"
QUESTION_URL = "skills.php?year="

# Grades/Topics ranging from 1st grade to High School Algebra 2.
GRADES = ["1", "2", "3", "4", "5", "6", "7", "8", "G", "S", "A1", "A2"]

# A mapping from grades/topics to relative difficulty, ranging from 1 to 10.
DIFFICULTIES = {
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "G": 9,
    "S": 10,
    "A1": 9,
    "A2": 10
}

driver = webdriver.Chrome("/usr/local/bin/chromedriver")


def create_problem(grade, curr_cat, ques):
    """Creates a maths problem given relevant information."""
    problem = {}
    problem["grade"] = grade
    problem["difficulty"] = DIFFICULTIES[grade]
    problem["category"] = curr_cat.text
    inner_ques = ques.find('a', href=True)
    problem["skillno"] = inner_ques['href']
    problem["question"] = inner_ques.text
    return problem


def get_relevant_elements(grade_url):
    """Retrieves any question category or question title elements from a web page."""
    grade_but = driver.find_element_by_xpath('//a[@href="' + grade_url + '"]')
    grade_but.click()
    sleep(2)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    elements = soup.findAll('div',
                            attrs={'class': ['skillSubjTitle', 'skillNo']})
    return elements


def main():
    """Retrieves maths problems via web scraping and stores them as json."""
    problems = []
    driver.get(SITE_URL + QUESTION_URL)
    for grade in GRADES:
        elements = get_relevant_elements(QUESTION_URL + grade)
        index = 0
        curr_cat = elements[index]
        while curr_cat is not None:
            index += 1
            while index < len(
                    elements) and elements[index]['class'][0] == 'skillNo':
                ques = elements[index]
                problem = create_problem(grade, curr_cat, ques)
                problems.append(problem)
                index += 1
            if index < len(elements):
                curr_cat = elements[index]
            else:
                curr_cat = None

    with open('data.json', 'w') as data_file:
        json.dump(problems, data_file)


if __name__ == "__main__":
    main()
