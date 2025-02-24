"use client";

import React, { useState, useEffect } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Label,
} from "recharts";
import { Search, Sparkles, TrendingUp, Zap } from "lucide-react";
import { motion } from "framer-motion";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";


interface ProcessedRow {
  Trend: string;  // Maps to "name" in the API
  "Startup Opportunity": string;  // Maps to "Startup_Opportunity" or "description"
  "Related Trends": string;  // Maps to "Related_trends"
  "Growth Rate, WoW": number;  // Maps to "Growth_rate_WoW"
  "YC Chances": number;  // Maps to "YC_chances"
  "2025": number;  // Maps to "Year_2025"
  "2026": number;  // Maps to "Year_2026"
  "2027": number;  // Maps to "Year_2027"
  "2028": number;  // Maps to "Year_2028"
  "2029": number;  // Maps to "Year_2029"
  "2030": number;  // Maps to "Year_2030"
  [key: string]: string | number;
}

const years = ["2025", "2026", "2027", "2028", "2029", "2030"];

const colors = [
  "#6366f1", // Indigo
  "#ec4899", // Pink
  "#06b6d4", // Cyan
  "#f59e0b", // Amber
  "#10b981", // Emerald
  "#8b5cf6", // Violet
  "#f43f5e", // Rose
  "#3b82f6", // Blue
  "#84cc16", // Lime
  "#14b8a6", // Teal
];

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0];
    return (
      <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-100">
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 rounded-full" style={{ backgroundColor: data.stroke }} />
          <span className="font-medium text-sm">{data.name}</span>
        </div>
        <p className="text-sm text-gray-600 mt-1">
          {label}: {data.value}%
        </p>
      </div>
    );
  }
  return null;
};

// YC Companies mapping
type YCCompanyInfo = {
  name: string;
  logo: string;
};

type YCTrends = "Personalized Neurostimulation" | "VR/AR/MR for Immersive Experiences";

const ycCompanies: Record<YCTrends, readonly YCCompanyInfo[]> = {
  "Personalized Neurostimulation": [
    { name: "Neuralink", logo: "/company-logos/neuralink.png" },
    { name: "Kernel", logo: "/company-logos/kernel.png" }
  ],
  "VR/AR/MR for Immersive Experiences": [
    { name: "Magic Leap", logo: "/company-logos/magic-leap.png" },
    { name: "Mojo Vision", logo: "/company-logos/mojo-vision.png" }
  ]
} as const;

const CompanyLogo = ({ src, name }: { src: string; name: string }) => {
  const [error, setError] = useState(false);
  const initials = name
    .split(" ")
    .map(word => word[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);

  if (error) {
    return (
      <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
        <span className="text-xs font-medium text-blue-600">{initials}</span>
      </div>
    );
  }

  return (
    <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center overflow-hidden">
      <img
        src={src}
        alt={`${name} logo`}
        className="w-full h-full object-cover"
        onError={() => setError(true)}
      />
    </div>
  );
};

export default function Home() {
  const [trendsData, setTrendsData] = useState<ProcessedRow[]>([]);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [selectedTrend, setSelectedTrend] = useState<ProcessedRow | null>(null);
  const [filteredData, setFilteredData] = useState<ProcessedRow[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);



  const fetchTrends = async () => {
    setIsLoading(true);
    setError(null);
    try {
      console.log("Sending request to API...");
      const response = await fetch("https://simple-lobster-morally.ngrok-free.app/analyze", {
        method: "POST",
        headers: {
          accept: "application/json",
          "Content-Type": "application/json",
          "ngrok-skip-browser-warning": "1"
        },
        mode: "cors",
        body: JSON.stringify({
          generate_novel_ideas: true,
          user_input: searchQuery || "new uses for ai",
          k: 5
        })
      });
  
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status} - ${response.statusText}`);
      }
  
      console.log("Response received, parsing JSON...");
      const data = await response.json();
      console.log("Raw API Response:", data);
  
      if (
        data.data &&  // Note: Changed from data.data to data
        data.data.final_result &&
        Array.isArray(data.data.final_result.trends)
      ) {
        console.log("Setting trend data with", data.data.final_result.trends.length, "trends");
        
        const processedTrends = data.data.final_result.trends.map((trend: any) => ({
          Trend: trend.name || "Unknown Trend",
          "Startup Opportunity": trend.Startup_Opportunity || trend.description || "Unknown Opportunity",
          "Related Trends": trend.Related_trends || "",
          "Growth Rate, WoW": trend.Growth_rate_WoW || 0,  // Already a number, no parseFloat needed
          "YC Chances": trend.YC_chances || 0,  // Already a number, no parseFloat needed
          "2025": trend.Year_2025 || 0,
          "2026": trend.Year_2026 || 0,
          "2027": trend.Year_2027 || 0,
          "2028": trend.Year_2028 || 0,
          "2029": trend.Year_2029 || 0,
          "2030": trend.Year_2030 || 0,
        })) as ProcessedRow[];
  
        setTrendsData(processedTrends);
        setFilteredData(processedTrends);
        if (processedTrends.length > 0) {
          console.log("Setting selected trend:", processedTrends[0]);
          setSelectedTrend(processedTrends[0]);
        }
      } else {
        throw new Error("Invalid data format received from API or no trends found");
      }
    } catch (err: any) {
      console.error("Error fetching trends:", err);
      setError(err.message || "Unknown error");
      setTrendsData([]);
      setFilteredData([]);
      setSelectedTrend(null);
    } finally {
      setIsLoading(false);
    }
  };
  
  useEffect(() => {
    const timer = setTimeout(() => {
      fetchTrends();
    }, 500);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  const pivotedData = years.map((year) => {
    const obj: { year: string; [key: string]: number | string } = { year };
    filteredData.forEach((row) => {
      obj[row.Trend] = row[year as keyof ProcessedRow];
    });
    return obj;
  });

  const handleMouseMove = (state: any) => {
    if (state?.activePayload?.[0]) {
      const trendName = state.activePayload[0].dataKey;
      const selected = filteredData.find((row) => row.Trend === trendName);
      if (selected) {
        console.log("Selected trend:", selected.Trend);
        setSelectedTrend(selected);
      }
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="h-16 bg-white shadow-sm border-b sticky top-0 z-50">
        <div className="max-w-[1920px] mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-2">
              <Sparkles className="h-6 w-6 text-indigo-600" />
              <h1 className="text-xl font-semibold text-gray-900">
                SpyGlass Trends
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  type="text"
                  placeholder="Search trends..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 w-64"
                />
              </div>
              <Button variant="default" onClick={() => fetchTrends()}>
                <Sparkles className="h-4 w-4 mr-2" />
                Generate Report
              </Button>
            </div>
          </div>
        </div>
      </header>

      {isLoading ? (
        <div className="flex items-center justify-center h-[calc(100vh-64px)]">
          <div className="text-center">
            <div className="w-16 h-16 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading data...</p>
          </div>
        </div>
      ) : error ? (
        <div className="flex items-center justify-center h-[calc(100vh-64px)]">
          <div className="text-center text-red-600 p-4 rounded-lg">
            <h3 className="text-lg font-semibold mb-2">Error Loading Data</h3>
            <p>{error}</p>
            <Button
              onClick={() => fetchTrends()}
              className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
            >
              Try Again
            </Button>
          </div>
        </div>
      ) : (
        <main className="h-[calc(100vh-64px)] px-2 fixed w-full overflow-hidden">
          <div className="flex gap-4 h-full max-w-[1920px] mx-auto">
            {/* Left Legend */}
            <div className="w-72 shrink-0">
              <Card className="h-full bg-white">
                <CardHeader>
                  <CardTitle className="text-sm font-medium text-gray-500">
                    Trend Categories
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {filteredData.map((trend, idx) => (
                    <div
                      key={trend.Trend}
                      className="flex items-start space-x-2.5 px-2 py-1.5 rounded-md hover:bg-gray-50"
                    >
                      <div
                        className="w-2.5 h-2.5 rounded-full mt-1.5 shrink-0"
                        style={{ backgroundColor: colors[idx % colors.length] }}
                      />
                      <span className="text-sm text-gray-700 break-words overflow-wrap-anywhere leading-tight">
                        {trend.Trend}
                      </span>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>

            {/* Center Content */}
            <div className="flex-1 flex flex-col gap-4">
              {/* Chart */}
              <Card className="bg-white">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-xl font-semibold text-gray-900">
                      Technology Adoption Trends
                    </CardTitle>
                    <Select defaultValue="5y">
                      <SelectTrigger className="w-32">
                        <SelectValue placeholder="Time Range" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="5y">5 Years</SelectItem>
                        <SelectItem value="3y">3 Years</SelectItem>
                        <SelectItem value="1y">1 Year</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="h-[400px]">
                    <ResponsiveContainer>
                      <LineChart
                        data={pivotedData}
                        onMouseMove={handleMouseMove}
                        margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" opacity={0.4} />
                        <XAxis
                          dataKey="year"
                          tick={{ fontSize: 12, fill: "#6B7280" }}
                          tickLine={false}
                          axisLine={{ stroke: "#E5E7EB" }}
                        >
                          <Label
                            value="Timeline (Years)"
                            position="bottom"
                            style={{ fill: "#6B7280", fontSize: 12 }}
                          />
                        </XAxis>
                        <YAxis
                          domain={[0, 100]}
                          tickLine={false}
                          axisLine={{ stroke: "#E5E7EB" }}
                          tick={{ fontSize: 12, fill: "#6B7280" }}
                          tickFormatter={(value) => `${value}%`}
                        >
                          <Label
                            value="Market Adoption (%)"
                            angle={-90}
                            position="left"
                            style={{ fill: "#6B7280", fontSize: 12 }}
                          />
                        </YAxis>
                        <Tooltip content={<CustomTooltip />} cursor={false} />
                        {filteredData.map((trend, idx) => (
                          <Line
                            key={trend.Trend}
                            type="monotone"
                            dataKey={trend.Trend}
                            stroke={colors[idx % colors.length]}
                            strokeWidth={selectedTrend?.Trend === trend.Trend ? 3 : 1.5}
                            dot={false}
                            activeDot={{
                              r: 6,
                              fill: colors[idx % colors.length],
                              stroke: "white",
                              strokeWidth: 2,
                            }}
                            opacity={selectedTrend ? (selectedTrend.Trend === trend.Trend ? 1 : 0.2) : 1}
                          />
                        ))}
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>

              {/* Opportunities List - Scrollable */}
              <div className="overflow-auto flex-1" style={{ maxHeight: "calc(100vh - 580px)" }}>
                <div className="grid grid-cols-2 gap-4 pb-4">
                  {filteredData.map((trend, idx) => (
                    <motion.div
                      key={trend.Trend}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: idx * 0.1 }}
                    >
                      <Card
                        className={`cursor-pointer transition-all hover:shadow-lg bg-white ${
                          selectedTrend?.Trend === trend.Trend ? "ring-2 ring-indigo-500" : ""
                        }`}
                        onClick={() => setSelectedTrend(trend)}
                        onMouseEnter={() => setSelectedTrend(trend)}
                      >
                        <CardContent className="p-4">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <h3 className="font-semibold text-gray-900">
                                {trend["Startup Opportunity"]}
                              </h3>
                              <p className="text-sm text-gray-500 mt-1">
                                {trend.Trend}
                              </p>
                            </div>
                            <Badge className="bg-indigo-50 text-indigo-700 flex items-center space-x-1 ml-2 shrink-0">
                              <TrendingUp className="h-3 w-3" />
                              <span>{trend["Growth Rate, WoW"]} WoW</span>
                            </Badge>
                          </div>
                        </CardContent>
                      </Card>
                    </motion.div>
                  ))}
                </div>
              </div>
            </div>

            {/* Right Details Panel */}
            <div className="w-80 shrink-0">
              <Card className="h-full bg-white">
                <CardHeader>
                  <CardTitle className="text-gray-900">Trend Details</CardTitle>
                </CardHeader>
                <CardContent>
                  {selectedTrend ? (
                    <div className="space-y-6">
                      <div>
                        <h2 className="text-xl font-semibold text-gray-900">{selectedTrend.Trend}</h2>
                        <p className="mt-2 text-gray-500">{selectedTrend["Startup Opportunity"]}</p>
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <Card className="bg-gray-50">
                          <CardContent className="p-4">
                            <div className="flex items-center space-x-2">
                              <TrendingUp className="h-4 w-4 text-green-500" />
                              <div>
                                <p className="text-sm text-gray-500">Growth Rate, WoW</p>
                                <p className="font-semibold text-gray-900">
                                  {selectedTrend["Growth Rate, WoW"]}
                                </p>
                              </div>
                            </div>
                          </CardContent>
                        </Card>

                        <Card className="bg-gray-50">
                          <CardContent className="p-4">
                            <div className="flex items-center space-x-2">
                              <Zap className="h-4 w-4 text-yellow-500" />
                              <div>
                                <p className="text-sm text-gray-500">YC Chances</p>
                                <p className="font-semibold text-gray-900">
                                  {selectedTrend["YC Chances"]}
                                </p>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      </div>

                      <div>
                        <h3 className="font-medium text-gray-900 mb-2">Related Trends</h3>
                        <div className="flex flex-wrap gap-2">
                          {selectedTrend["Related Trends"].split(",").map((trend) => (
                            <Badge key={trend.trim()} className="bg-gray-100 text-gray-700">
                              {trend.trim()}
                            </Badge>
                          ))}
                        </div>
                      </div>

                      <div>
                        <h3 className="font-medium text-gray-900 mb-2">
                          YC-Funded Companies
                        </h3>
                        <div className="flex flex-col space-y-2">
                          {selectedTrend && ycCompanies[selectedTrend.Trend as YCTrends]?.map((company) => (
                            <div
                              key={company.name}
                              className="flex items-center p-2 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                            >
                              <CompanyLogo src={company.logo} name={company.name} />
                              <span className="ml-3 text-sm font-medium text-gray-900">
                                {company.name}
                              </span>
                            </div>
                          ))}
                          {selectedTrend && !ycCompanies[selectedTrend.Trend as YCTrends] && (
                            <div className="text-sm text-gray-500">
                              No YC companies found for this trend
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="flex items-center justify-center h-full text-gray-500">
                      Select a trend to view details
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        </main>
      )}
    </div>
  );
}
