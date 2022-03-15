import React from "react";
import styles from '../styles/Question.module.css'

export default function Question(){
    return(
        <div className={styles.container}>
            <h2 className={styles.title}>Question Page</h2>
            <p className={styles.description}>
            Hello World.
            </p>
        </div>
    )
}