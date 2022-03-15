import { React, useState, useEffect } from "react";
export default function Question() {
    const [data, setData] = useState(null)
    const [isLoading, setLoading] = useState(false)

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
            {data.map(function (q, index) {
                return <p key={index}>{q.question}</p>;
            })}
        </div>
    )
}