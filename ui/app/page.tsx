"use client";

import React, { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

interface Opportunity {
  title: string;
  relatedTrends: string;
  growth: string;
}

const opportunitiesData: Opportunity[] = [
  {
    title: 'Cheaper Air Filters',
    relatedTrends: 'Cats per capita, average income',
    growth: '10%',
  },
  {
    title: 'Free Cats for All',
    relatedTrends: 'Pet adoption rate, average income',
    growth: '15%',
  },
  {
    title: 'Bar',
    relatedTrends: 'Nightlife popularity, local events',
    growth: '12%',
  },
];

const chartData = [
  { name: '2025 Q1', redLine: 100, greenLine: 120, blackLine: 50, purpleLine: 80 },
  { name: '2025 Q2', redLine: 110, greenLine: 130, blackLine: 55, purpleLine: 82 },
  { name: '2025 Q3', redLine: 105, greenLine: 125, blackLine: 60, purpleLine: 90 },
  { name: '2025 Q4', redLine: 115, greenLine: 140, blackLine: 65, purpleLine: 95 },
];

export default function Home() {
  const [selectedOpportunity, setSelectedOpportunity] = useState<string>('Cheaper Air Filters');

  return (
    <div className="min-h-screen bg-gray-100 text-gray-800">
      {/* Top Navigation/Header */}
      <header className="w-full bg-white shadow-md p-4 flex items-center justify-between">
        <div className="mx-auto flex-1 max-w-xl">
          <input
            type="text"
            placeholder="Some Text"
            className="border border-gray-300 rounded-lg px-4 py-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-300 transition duration-200"
          />
        </div>
        <div className="flex space-x-2 ml-4">
          <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition duration-200 shadow-md focus:outline-none focus:ring-2 focus:ring-blue-300">
            Button 1
          </button>
          <button className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition duration-200 shadow-md focus:outline-none focus:ring-2 focus:ring-green-300">
            Button 2
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <div className="p-4 flex flex-col md:flex-row gap-4">
        {/* Left Column: Graph + Opportunities */}
        <div className="flex-1 flex flex-col space-y-4">
          {/* Graph Area */}
          <div className="bg-white shadow-lg rounded-lg p-4">
            <div className="flex">
              {/* Legend on the left */}
              <div className="w-1/4 pr-4 flex flex-col space-y-4">
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 bg-red-500 rounded-full" />
                  <span className="text-sm">Average household income in the United States</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 bg-green-500 rounded-full" />
                  <span className="text-sm">Average cost of [Insurance - implied] in California</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 bg-black rounded-full" />
                  <span className="text-sm">Wild fires per year</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 bg-purple-500 rounded-full" />
                  <span className="text-sm">Another data series</span>
                </div>
              </div>
              {/* Chart on the right */}
              <div className="w-3/4">
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={chartData}>
                    <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="redLine" stroke="#ff0000" strokeWidth={2} />
                    <Line type="monotone" dataKey="greenLine" stroke="#00ff00" strokeWidth={2} />
                    <Line type="monotone" dataKey="blackLine" stroke="#000000" strokeWidth={2} />
                    <Line type="monotone" dataKey="purpleLine" stroke="#800080" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
                <p className="text-xs text-gray-600 mt-2 italic">y axis = different for each line, defined in a legend somewhere.</p>
              </div>
            </div>
          </div>

          {/* Opportunity List */}
          <div className="bg-white shadow-lg rounded-lg p-4 h-64 overflow-auto">
            <h2 className="text-lg font-semibold mb-2">Opportunities</h2>
            <ul className="space-y-2">
              {opportunitiesData.map((op) => (
                <li
                  key={op.title}
                  className={
                    `border p-3 rounded-lg cursor-pointer transition duration-200 hover:shadow-md hover:bg-gray-50 ${
                      selectedOpportunity === op.title ? 'bg-gray-100' : ''
                    }`
                  }
                  onClick={() => setSelectedOpportunity(op.title)}
                >
                  <div className="font-semibold text-gray-800">{op.title}</div>
                  <div className="text-sm text-gray-600">Related Trends: {op.relatedTrends}</div>
                  <div className="text-sm">Anticipated Growth: {op.growth}</div>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Right Side Panel: Selected Opportunity Description */}
        <div className="w-full md:w-1/3 bg-white shadow-lg rounded-lg p-4">
          <h2 className="text-lg font-bold mb-2">Startup Opportunity: Fire safety pants</h2>
          <p className="text-sm leading-relaxed text-gray-700">
            Due to increase in household income and decrease in ilable fire Iraunince we forecast a 10% increase in
            household need for fire protection.
          </p>
        </div>
      </div>
    </div>
  );
}