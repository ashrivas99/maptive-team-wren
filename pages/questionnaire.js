import { React, useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/router";

export default function Questionnaire() {

  const router = useRouter();
  
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
            return (
            <div className="flex items-center space-x-3">
                <p className="text-green-500 text-lg font-bold">You are correct! The answer is {answer}</p>
                <p className="text-3xl">🙌</p>
            </div>)
        }
        else {
            return (
            <div className="flex items-center space-x-3">
                <p className="text-red-500 text-lg font-bold">You are incorrect! The answer was {answer}</p>
                <p className="text-3xl">😢</p>
            </div>)
        }
    }
    return <div></div>
  }

  function NextButton() {
    if (index == numQues - 1) {
      return (
        <div className="flex items-center justify-center mt-7">
          <button className="px-4 py-2 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500" 
                  onClick={changeQuestion}> Finish! </button>
        </div>)
    } 
    
    else 
    {
      return (
        <div className="flex items-center justify-center mt-7">
          <button className="px-4 py-2 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500" 
                  onClick={changeQuestion}> Next Question! </button>
        </div>)
    }
  }

  function Options() {
    return (
        // <div>
        //     {answers.map((item, ind) => (
        //         <div key={ind}>
        //             {answerTextExists(data[index], item) && <button onClick={() => checkAnswer(item)}>{data[index].mcq[item]["a_text"]}</button>}
        //             {answerImageExists(data[index], item) && <img src={"https://mathopolis.com/questions/" + data[index].mcq[item]["a_image"]}></img>}
        //         </div>
        //     ))}
        // </div>
        <div className="mt-5">
            <label className="text-base font-medium text-gray-900">Possible answers for the question</label>
            <p className="text-sm leading-5 text-gray-500">Choose one of the answers below:</p>
            <fieldset className="mt-4">
                <legend className="sr-only">Select answer</legend>
                <div className="space-y-4">
                    {answers.map((answerOption, ind) => (
                        <div key={ind} className="flex items-center">
                            <input onClick={() => {
                                if (answerTextExists(data[index], answerOption)){
                                    checkAnswer(answerOption)
                                }
                                
                            }}
                                id={ind}
                                name="answer-selection"
                                type="radio"
                                //defaultChecked={answerOption.id === 'email'}
                                className="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300"
                            />
                            {answerTextExists(data[index], answerOption) && <label htmlFor={ind} className="ml-3 block text-sm font-medium text-gray-700">
                                                                                {data[index].mcq[answerOption]["a_text"]}
                                                                            </label>}
                            

                            {answerImageExists(data[index], answerOption) && <label htmlFor={ind} className="ml-3 block text-sm font-medium text-gray-700">
                                                                                {data[index].mcq[answerOption]["a_text"]}
                                                                            </label>}
                        </div>
                    ))}
                </div>
            </fieldset>
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
      fetch("http://localhost:5000/pickQuestionnaireQuestions", {
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
  // if (grade != 0)  original
    // return (
    //   <div className="">
    //     <p>We have calculated that you are grade {grade}</p>
    //     <button onClick={() => router.push("/")}>Return to sign-up page</button>
    //   </div>
    // );
    return (
      <div className="bg-gray-100 h-screen mx-auto flex items-center justify-center">
        <div className="bg-white shadow-2xl sm:rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-blue-700">Grade {grade}</h3>
            <div className="mt-2 max-w-xl text-sm text-gray-500">
              <p>We have calculated that you are grade {grade}</p>
            </div>
            <div className="mt-5">
              <button
                onClick={() => router.push("/")}
                type="button"
                className="inline-flex items-center justify-center px-4 py-2 border border-transparent font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 sm:text-sm"
              >
                Return to sign-up page
              </button>
            </div>
          </div>
        </div>
      </div>
    )

  return (
    <div className="h-screen flex items-center justify-center">
        <div>
            {textExists(data[index]) && <p className="text-center p-5 text-2xl font-bold text-indigo-700">{data[index].mcq.q_text}</p>}
            {imageExists(data[index]) && <img src={"https://mathopolis.com/questions/" + data[index].mcq.q_image}></img>}
            <Options></Options>
            <Answer></Answer>
            <NextButton></NextButton>
        </div>
    
    </div>
  )
}


