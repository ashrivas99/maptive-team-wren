import { React, useState, useEffect } from "react";
import Link from "next/link";

export default function Questionnaire() {
  const [data, setData] = useState(null);
  const [numCorrect, setNumCorrect] = useState(0);
  const [grade, setGrade] = useState(0);
  const [isLoading, setLoading] = useState(false);
  const [index, setIndex] = useState(0);
  const [numQues, setNumQues] = useState(0);
  const answers = ["A", "B", "C", "D"];
  let [displayAnswer, setDisplayAnswer] = useState("false");
  let [correct, setCorrect] = useState("false");
  let [answer, setAnswer] = useState("A");
  let username = "";

  function changeQuestion() {
    setDisplayAnswer(false);
    if (index < numQues - 1) {
      setIndex(index + 1);
      setQuestion(data);
    } else {
      setGrade(numCorrect >= 10 ? 10 : numCorrect + 1);
    }
  }

  function textExists(question) {
    const value = question?.mcq?.q_text;
    if (value !== undefined) {
      return true;
    }
    return false;
  }

  function imageExists(question) {
    const value = question?.mcq?.q_image;
    if (value !== undefined) {
      return true;
    }
    return false;
  }

  function answerTextExists(answer, letter) {
    let value = answer?.mcq;
    if (value !== undefined) {
      value = value[letter]?.a_text;
      if (value !== undefined) {
        return true;
      }
    }
    return false;
  }

  function answerImageExists(answer, letter) {
    let value = answer?.mcq;
    if (value !== undefined) {
      value = value[letter]?.a_image;
      if (value !== undefined && value != "") {
        return true;
      }
    }
    return false;
  }

  function checkAnswer(attempt) {
    setDisplayAnswer(true);
    correct = setCorrect(attempt == answer);
    if (attempt == answer) {
      setNumCorrect(numCorrect + 1);
    }
  }

  function Answer() {
    if (displayAnswer == true) {
      if (correct == true) {
        return <p>You are correct! The answer is {answer}</p>;
      } else {
        return <p>You were incorrect. The answer is {answer}</p>;
      }
    }
    return <div></div>;
  }

  function NextButton() {
    if (index == numQues - 1) {
      return <button onClick={changeQuestion}>Finish</button>;
    } else {
      return <button onClick={changeQuestion}>Next Question</button>;
    }
  }

  function Options() {
    return (
      <div>
        {answers.map((item, ind) => (
          <div key={ind}>
            {answerTextExists(data[index], item) && (
              <button onClick={() => checkAnswer(item)}>
                {data[index].mcq[item]["a_text"]}
              </button>
            )}
            {answerImageExists(data[index], item) && (
              <img
                onClick={() => checkAnswer(item)}
                src={
                  "https://mathopolis.com/questions/" +
                  data[index].mcq[item]["a_image"]
                }
              ></img>
            )}
          </div>
        ))}
      </div>
    );
  }

  function setQuestion(questions) {
    if (questions[index].mcq["A"]["correct"] == true) {
      setAnswer("A");
    }
    if (questions[index].mcq["B"]["correct"] == true) {
      setAnswer("B");
    }
    if (questions[index].mcq["C"]["correct"] == true) {
      setAnswer("C");
    }
    if (questions[index].mcq["D"]["correct"] == true) {
      setAnswer("D");
    }
    setLoading(false);
  }

  useEffect(() => {
    username = localStorage.getItem("user");
    setLoading(true);
    if (numQues == 0) {
      fetch("http://localhost:5000/pick_questionnaire_questions", {
        method: "GET",
        mode: "cors",
      })
        .then((res) => res.json())
        .then((data) => {
          setData(data.data);
          setNumQues(data.data.length);
          setQuestion(data.data);
        });
    } else {
      setQuestion(data);
    }
  }, []);

  if (isLoading) return <p>Loading...</p>;
  if (!data) return <p>No profile data</p>;
  if (grade != 0)
    return (
      <div>
        <p>We have calculated that you are grade {grade}</p>
        <Link href="/">
          <a>
            <button>Return to sign-up page</button>
          </a>
        </Link>
      </div>
    );

  return (
    <div>
      <div>
        <div>
          {textExists(data[index]) && <p>{data[index].mcq.q_text}</p>}
          {imageExists(data[index]) && (
            <img
              src={
                "https://mathopolis.com/questions/" + data[index].mcq.q_image
              }
            ></img>
          )}
          <Options></Options>
          <Answer></Answer>
          <NextButton></NextButton>
        </div>
      </div>
    </div>
  );
}
