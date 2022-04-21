import { React, useState, useEffect } from "react";
export default function Question() {
    const [data, setData] = useState(null)
    const [isLoading, setLoading] = useState(false)
    const [index, setIndex] = useState(0);
    const answers = ["A", "B", "C", "D"];
    let [displayAnswer, setDisplayAnswer] = useState("false");
    let [correct, setCorrect] = useState("false");
    let [answer, setAnswer] = useState("A");
    const [userName, setUserName] = useState(null)

    useEffect(() => {
        // Perform localStorage action
        setUserName(localStorage.getItem("user"))
      }, [])


    function changeQuestion() {
        setDisplayAnswer(false)
        fetch('http://localhost:5000/pickQuestionnaireQuestions', {
            method: 'POST',
            mode: 'cors',
            body: JSON.stringify(
                { "question": data[index], "correct": correct, "username": username }
            ),
        })
            .then((res) => res.json())
            .then((data) => {
                setIndex(data.index);
            })
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
        setDisplayAnswer(true)
        correct = setCorrect(attempt == answer)
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
        setLoading(false)
    }

    useEffect(() => {
        setLoading(true)
        if (data == null) {
            fetch('http://localhost:5000/questionData', {
                method: 'GET',
                mode: 'cors'
            })
                .then((res) => res.json())
                .then((data) => {
                    setData(data.data)
                    setQuestion(data.data)
                })
        }
        else {
            setQuestion(data)
        }
    }, [])

    if (isLoading) return <p>Loading...</p>
    if (!data) return <p>No profile data</p>

    return (
            <div className="h-screen flex items-center justify-center">
                <div>
                    {textExists(data[index]) && <p className="text-center p-5 text-2xl font-bold text-indigo-700">{data[index].mcq.q_text}</p>}
                    {imageExists(data[index]) && <img src={"https://mathopolis.com/questions/" + data[index].mcq.q_image}></img>}
                    <Options></Options>
                    <Answer></Answer>
                    <div className="flex items-center justify-center mt-7">
                        <button className="px-4 py-2 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500" 
                                onClick={changeQuestion}> new question! </button>
                    </div>
                </div>
            
            </div>
    )
}