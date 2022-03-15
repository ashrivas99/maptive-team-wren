import { React, useState, useEffect } from "react";
export default function Question() {
    const [data, setData] = useState(null)
    const [isLoading, setLoading] = useState(false)
    const [index, setIndex] = useState(0);

    function changeQuestion() {
        let newIndex = Math.floor(Math.random() * (data.length - 0) + 0);
        setIndex(newIndex);
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
                setLoading(false)
            })
    }, [])

    if (isLoading) return <p>Loading...</p>
    if (!data) return <p>No profile data</p>

    return (
        <div>
            <p>{data[index].question}</p>
            <button onClick={changeQuestion}> new question! </button>
        </div>
    )
}