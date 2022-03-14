import React, { Fragment, useState  } from "react";
import { Listbox, Transition } from '@headlessui/react'
import { CheckIcon, SelectorIcon } from '@heroicons/react/solid'

const people = [
    { id: 1, name: 'Grade 1' },
    { id: 2, name: 'Grade 2' },
    { id: 3, name: 'Grade 3' },
    { id: 4, name: 'Grade 4' },
    { id: 5, name: 'Grade 5' },
    { id: 6, name: 'Grade 6' },
    { id: 7, name: 'Grade 7' },
    { id: 8, name: 'Grade 8' },
    { id: 9, name: 'Grade 9' },
    { id: 10, name: 'Grade 10' },
  ]
  
  function classNames(...classes) {
    return classes.filter(Boolean).join(' ')
}
  
export default function Form() {
    const [name, setName] = useState("");
    // const [gradeLevel, setGradeLeve;]
    const [selected, setSelected] = useState(people[3])

    return (
      <div className='max-w-3xl mx-auto bg-blue-200 p-20 rounded-3xl flex-col space-y-5'>
        <div>
            <label htmlFor="name" className="ml-px pl-4 block text-sm font-medium text-gray-700">
            Name
            </label>
            <div className="mt-1">
            <input
                type="text"
                name="name"
                id="name"
                className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 px-4 py-2 rounded-full"
                placeholder="Please provide your name..."
                value={name}
                onChange = {(e) => setName(e.target.value)}
            />
            </div>
        </div>
        <div>
            <Listbox value={selected} onChange={setSelected}>
            {({ open }) => (
                <>
                <Listbox.Label className="block text-sm font-medium text-gray-700">Select a Grade</Listbox.Label>
                <div className="mt-1 relative">
                    <Listbox.Button className="relative w-full bg-white border border-gray-300 rounded-md shadow-sm pl-3 pr-10 py-2 text-left cursor-default focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
                    <span className="block truncate">{selected.name}</span>
                    <span className="absolute inset-y-0 right-0 flex items-center pr-2 pointer-events-none">
                        <SelectorIcon className="h-5 w-5 text-gray-400" aria-hidden="true" />
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
                        {people.map((person) => (
                        <Listbox.Option
                            key={person.id}
                            className={({ active }) =>
                            classNames(
                                active ? 'text-white bg-indigo-600' : 'text-gray-900',
                                'cursor-default select-none relative py-2 pl-8 pr-4'
                            )
                            }
                            value={person}
                        >
                            {({ selected, active }) => (
                            <>
                                <span className={classNames(selected ? 'font-semibold' : 'font-normal', 'block truncate')}>
                                {person.name}
                                </span>

                                {selected ? (
                                <span
                                    className={classNames(
                                    active ? 'text-white' : 'text-indigo-600',
                                    'absolute inset-y-0 left-0 flex items-center pl-1.5'
                                    )}
                                >
                                    <CheckIcon className="h-5 w-5" aria-hidden="true" />
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
        </div>
      </div>
    )
  }