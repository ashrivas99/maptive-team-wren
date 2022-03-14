"""Web Scraping module."""
import json
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException

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

service = Service("/usr/local/bin/chromedriver")
driver = webdriver.Chrome(service=service)


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


def get_relevant_soup(curr_url):
    """Retrieves any question category or question title elements from a web page."""
    grade_but = driver.find_element(By.XPATH, '//a[@href="' + curr_url + '"]')
    try:
        grade_but.click()
    except ElementClickInterceptedException:
        grade_but.click()
    sleep(0.5)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    return soup


def click_options():
    """Clicks MCQ options in order to cause the correct answer to be highlighted."""
    i = 0
    while i < 4:
        try:
            driver.find_element(By.XPATH, "//div[@id='" + "adiv" + str(i) +
                                "']").click()
            sleep(0.5)
            return
        except ElementClickInterceptedException:
            i += 1


def create_option(opt_content, found_answer):
    """Creates an MCQ option given relevant information."""
    option = {}
    a_text = opt_content.find('p').text if opt_content.find('p') else ""
    a_img = opt_content.find('img')["src"] if opt_content.find('img') else ""
    correct = False

    if not found_answer:
        if opt_content["style"].find("border: 2px solid rgb(0, 255, 0)") != -1:
            correct = True
            found_answer = True

    option = {"correct": correct, "a_text": a_text, "a_image": a_img}
    return option, found_answer


def main():
    """Retrieves maths problems via web scraping and stores them as json."""
    problems = []
    driver.get(SITE_URL + QUESTION_URL)
    for grade in GRADES:
        soup = get_relevant_soup(QUESTION_URL + grade)
        elements = soup.findAll('div',
                                attrs={'class': ['skillSubjTitle', 'skillNo']})
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

    choices = ["A", "B", "C", "D"]
    for problem in problems:

        # Must reset the driver to start from the home page again.
        driver.get(SITE_URL + QUESTION_URL)
        soup = get_relevant_soup(QUESTION_URL + problem["grade"])

        # Direct browser to the problem-specific page.
        soup = get_relevant_soup(problem["skillno"])
        question = soup.find('div', attrs={'class': 'question'})
        q_img = question.find('img')["src"] if question.find('img') else ""
        mcq = {"q_text": question.text, "q_image": q_img}

        # Click an option so the correct answer is highlighted green.
        click_options()
        soup = BeautifulSoup(driver.page_source, "html.parser")
        found_answer = False
        for i, choice in enumerate(choices):
            opt_content = soup.find('div', attrs={'id': 'adiv' + str(i)})
            option, found_answer = create_option(opt_content, found_answer)
            mcq[choice] = option
        problem["mcq"] = mcq

    with open('data.json', 'a') as data_file:
        json.dump(problems, data_file)


if __name__ == "__main__":
    main()
