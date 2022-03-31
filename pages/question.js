import { React, useState, useEffect } from "react";
export default function Question() {
    const [data, setData] = useState(null)
    const [isLoading, setLoading] = useState(false)
    const [index, setIndex] = useState(0);
    const answers = ["A", "B", "C", "D"];
    let [displayAnswer, setDisplayAnswer] = useState("false");
    let [correct, setCorrect] = useState("false");
    let answer = "A"
    let username = localStorage.getItem("user")

    function changeQuestion() {
        setDisplayAnswer(false)
        fetch('http://localhost:5000/pick_question', {
            method: 'POST',
            mode: 'cors',
            body: JSON.stringify(
                { "question": data[index], "correct": correct, "username": username }
            ),
        })
            .then((res) => res.json())
            .then((data) => {
                console.log(data.index)
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
                return (<p>You are correct! The answer is {answer}</p>)
            }
            else {
                return (<p>You were incorrect. The answer is {answer}</p>)
            }
        }
        return <div></div>
    }
    function Options() {
        return (
            <div>
                {answers.map((item, ind) => (
                    <div key={ind}>
                        {answerTextExists(data[index], item) && <button onClick={() => checkAnswer(item)}>{data[index].mcq[item]["a_text"]}</button>}
                        {answerImageExists(data[index], item) && <img src={"https://mathopolis.com/questions/" + data[index].mcq[item]["a_image"]}></img>}
                    </div>
                ))}
            </div>
        );
    }

    useEffect(() => {
        setLoading(true)
        fetch('http://localhost:5000/question_data', {
            method: 'GET',
            mode: 'cors'
        })
            .then((res) => res.json())
            .then((data) => {
                setData(data.data)
                if (data.data[index].mcq["A"]["correct"] == true) {
                    answer = "A"
                }
                if (data.data[index].mcq["B"]["correct"] == true) {
                    answer = "B"
                }
                if (data.data[index].mcq["C"]["correct"] == true) {
                    answer = "C"
                }
                if (data.data[index].mcq["D"]["correct"] == true) {
                    answer = "D"
                }
                setLoading(false)
            })
    }, [])

    if (isLoading) return <p>Loading...</p>
    if (!data) return <p>No profile data</p>

    return (
        <div>
            <div>
                <div>
                    {textExists(data[index]) && <p>{data[index].mcq.q_text}</p>}
                    {imageExists(data[index]) && <img src={"https://mathopolis.com/questions/" + data[index].mcq.q_image}></img>}
                    <Options></Options>
                    <Answer></Answer>
                    <button onClick={changeQuestion}> new question! </button>
                </div>
            </div>
        </div>
    )
}