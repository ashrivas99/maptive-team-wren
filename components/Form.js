import React, { Fragment, useState } from "react";
import { Listbox, Transition } from "@headlessui/react";
import { CheckIcon, SelectorIcon, StatusOfflineIcon } from "@heroicons/react/solid";
import Link from "next/link";

const grades = ["1", "2", "3", "4", "5", "6", "7", "8", "Geometry", "Statistics", "Algebra 1", "Algebra 2"]

function classNames(...classes) {
  return classes.filter(Boolean).join(" ");
}

export default function Form() {
  const [name, setName] = useState("");
  const [newUser, setNewUser] = useState(true);
  const [selectedCats, setSelectedCats] = useState([]);
  const [cats, setCats] = useState(
    ["Counting", "Addition", "Subtraction", "Numbers",
      "Geometry (Plane)", "Geometry (Solid)", "Pre-Algebra",
      "Estimation", "Probability", "Money"]
  );
  const [grade, setGrade] = useState(grades[0]);
  const [categoryBox, setCategoryBox] = useState(Categories(cats))

  const registerUser = async (name, grade) => {
    const success = true;

    let userData = {
      username: name,
      grade: parseInt(grade),
      categories: selectedCats
    };

    fetch("http://localhost:5000/registerUser", {
      method: "POST",
      mode: "cors",
      body: JSON.stringify(userData),
    })
      .then((res) => res.json())
      .then((data) => {
        console.log(data);
        localStorage.setItem("user", name);
      })
      .catch((error) => {
        console.error(error);
      });
  };

  function addCat(cat) {
    const index = selectedCats.indexOf(cat);
    if (index > -1) {
      selectedCats.splice(index, 1);
      setSelectedCats(selectedCats)
      const btn = document.getElementById(cat);
      btn.style.backgroundColor = 'lightblue';
    }
    else {
      selectedCats.push(cat);
      setSelectedCats(selectedCats)
      const btn = document.getElementById(cat);
      btn.style.backgroundColor = 'green';
    }
  }

  function makeButton(cat) {
    return (
      <button key={cat} id={cat} onClick={() => addCat(cat)}>
        {cat}
      </button>
    );
  }

  function stuff(value) {
    setGrade(value)
    fetch("http://localhost:5000/getCategories", {
      method: "POST",
      mode: "cors",
      body: JSON.stringify({ "grade": value }),
    })
      .then((res) => res.json())
      .then((data) => {
        setSelectedCats([])
        setCats(data.categories)
        setCategoryBox(Categories(data.categories))
      })
      .catch((error) => {
        console.error(error);
      });
  }

  function Categories(cats) {
    return (
      <div id="scrollbox">
        {cats.map(makeButton, this)}
      </div>
    )
  }

  function SignUp() {
    if (newUser == false) {
      return (<p> If you do not have an account: <button onClick={() => { setNewUser(true) }} className="inline-flex items-center px-4 py-2 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">Sign Up</button></p>)
    }
    else {
      return (
        <div>
          <Listbox id="lb" value={grade} onChange={(value) => stuff(value)}>
            {({ open }) => (
              <>
                <Listbox.Label className="block text-sm font-medium text-gray-700">
                  Select a Grade
                </Listbox.Label>
                <div className="mt-1 relative">
                  <Listbox.Button className="relative w-full bg-white border border-gray-300 rounded-md shadow-sm pl-3 pr-10 py-2 text-left cursor-default focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
                    <span className="block truncate">Grade {grade}</span>
                    <span className="absolute inset-y-0 right-0 flex items-center pr-2 pointer-events-none">
                      <SelectorIcon
                        className="h-5 w-5 text-gray-400"
                        aria-hidden="true"
                      />
                    </span>
                  </Listbox.Button>

                  <Transition
                    show={open}
                    as={Fragment}
                    leave="transition ease-in duration-100"
                    leaveFrom="opacity-100"
                    leaveTo="opacity-0"
                  >
                    <Listbox.Options className="absolute z-10 mt-1 w-full bg-white shadow-lg max-h-60 rounded-md py-1 text-base ring-1 ring-black ring-opacity-5 overflow-auto focus:outline-none sm:text-sm">
                      {grades.map((currGrade) => (
                        <Listbox.Option
                          key={currGrade}
                          className={({ active }) =>
                            classNames(
                              active
                                ? "text-white bg-indigo-600"
                                : "text-gray-900",
                              "cursor-default select-none relative py-2 pl-8 pr-4"
                            )
                          }
                          value={currGrade}
                        >
                          {({ selected, active }) => (
                            <>
                              <span
                                className={classNames(
                                  selected ? "font-semibold" : "font-normal",
                                  "block truncate"
                                )}
                              >
                                {currGrade}
                              </span>

                              {selected ? (
                                <span
                                  className={classNames(
                                    active ? "text-white" : "text-indigo-600",
                                    "absolute inset-y-0 left-0 flex items-center pl-1.5"
                                  )}
                                >
                                  <CheckIcon
                                    className="h-5 w-5"
                                    aria-hidden="true"
                                  />
                                </span>
                              ) : null}
                            </>
                          )}
                        </Listbox.Option>
                      ))}
                    </Listbox.Options>
                  </Transition>
                </div>
              </>
            )}
          </Listbox>
          <Link href="/questionnaire">
            <a>
            Don't know your grade? 
              <button className="inline-flex items-center px-4 py-2 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                Click here.
              </button>
            </a>
          </Link>
          <br></br>
          <br></br>
          <p>Pick some categories you are interested in for this grade</p>
          {categoryBox}
          <br></br>
          <p> If you already have an account: <button onClick={() => { setNewUser(false) }} className="inline-flex items-center px-4 py-2 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">Log-In</button></p>
        </div>
      )
    }
  }

  function Title() {
    if (newUser == true) {
      return (<p id="header">Register Page</p>)
    }
    else {
      return (<p id="header">Log-In Page</p>)
    }
  }
  return (
    <div className="max-w-3xl mx-auto bg-blue-200 p-20 rounded-3xl flex-col space-y-5">
      <Title></Title>
      <link href="https://fonts.googleapis.com/css?family=Baloo+2:400,800&display=swap" rel="stylesheet"></link>
      <div>
        <label
          htmlFor="name"
          className="ml-px block text-sm font-medium text-gray-700"
        >
          Username
        </label>
        <div className="mt-1">
          <input
            type="text"
            name="name"
            id="name"
            className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 px-4 py-2 rounded-full"
            placeholder="Please enter your username..."
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
        </div>
      </div>
      <div>
        <SignUp></SignUp>
        <br></br>
        <div className="flex justify-center items-center">
          <Link href="/question">
            <a>
              <button onClick={() => registerUser(name, grade)} className="inline-flex items-center px-4 py-2 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">Submit</button>
            </a>
          </Link>
        </div>
      </div>
    </div>
  );
}
