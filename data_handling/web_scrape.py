from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
import json

driver = webdriver.Chrome("/usr/local/bin/chromedriver")
site_url = "https://mathopolis.com/questions/"
question_url = "skills.php?year="
grades = ["1", "2", "3", "4", "5", "6", "7", "8", "G", "S", "A1", "A2"]
difficulties = {"1":1, "2":2, "3":3, "4":4, "5":5, "6":6, "7":7, "8":8, "G":9, "S":10, "A1":9, "A2":10}

def main():
    problems = []
    driver.get(site_url + question_url)
    for grade in grades:
        grade_url = question_url + grade
        grade_but= driver.find_element_by_xpath('//a[@href="'+ grade_url +'"]')
        grade_but.click()
        sleep(2)

        content = driver.page_source
        soup = BeautifulSoup(content, "html.parser")
        elements = soup.findAll('div', attrs={'class':['skillSubjTitle', 'skillNo']})
        index = 0
        curr_cat = elements[index]

        while curr_cat !=None:
            index+=1
            while index < len(elements) and elements[index]['class'][0] == 'skillNo':
                q = elements[index]
                problem = {}
                problem["difficulty"] = difficulties[grade]
                problem["category"] = curr_cat.text
                question = q.find('a', href=True)
                problem["skillno"] = question['href']
                problem["question"] = question.text
                problems.append(problem)
                index+=1
            if index < len(elements):
                curr_cat = elements[index]
            else:
                curr_cat = None   

    with open('data.json', 'w') as f:
        json.dump(problems, f)

if __name__ == "__main__":
    main()