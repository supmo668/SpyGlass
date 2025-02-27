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
import { Search, Sparkles, TrendingUp, Zap, Loader2 } from "lucide-react";
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import SearchInput from "@/components/SearchInput"; // Adjust path as needed
import "./styles.css"; // Adjust path if needed

interface ProcessedRow {
  Trend: string;
  "Startup Opportunity": string;
  "Related Trends": string;
  "Growth Rate, WoW": number;
  "YC Chances": number;
  "2025": number;
  "2026": number;
  "2027": number;
  "2028": number;
  "2029": number;
  "2030": number;
  [key: string]: string | number;
}

const years = ["2025", "2026", "2027", "2028", "2029", "2030"];
const colors = ["#6366f1", "#ec4899", "#06b6d4", "#f59e0b", "#10b981", "#8b5cf6", "#9333ea", "#f43f5e", "#14b8a6", "#eab308"];

const starterQueries = [
  "AI in Healthcare",
  "Green Energy Tech",
  "Next-Gen AR/VR",
  "Blockchain Uses",
  "Robotics Startups",
  "Space Tech",
];

const starterTrends = starterQueries.map((query, idx) => ({
  name: query,
  data: [
    { year: "2025", growth: Math.floor(Math.random() * 20) + 10 },
    { year: "2026", growth: Math.floor(Math.random() * 30) + 20 },
    { year: "2027", growth: Math.floor(Math.random() * 40) + 30 },
    { year: "2028", growth: Math.floor(Math.random() * 50) + 40 },
    { year: "2029", growth: Math.floor(Math.random() * 60) + 50 },
    { year: "2030", growth: Math.floor(Math.random() * 70) + 60 },
  ],
}));

interface TrendDataPoint {
  year: string;
  growth: number;
}

interface TrendItem {
  name: string;
  data: TrendDataPoint[];
}

interface TrendChartProps {
  trendsData: TrendItem[];
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<any>;
  label?: string;
}

interface ChartDataPoint {
  year: string;
  [key: string]: string | number;
}

const TrendChart = ({ trendsData }: TrendChartProps) => {
  const chartData = trendsData[0]?.data.map((item) => {
    const dataPoint: ChartDataPoint = { year: item.year };
    trendsData.forEach((trend) => {
      dataPoint[trend.name] = trend.data.find((d) => d.year === item.year)?.growth || 0;
    });
    return dataPoint;
  }) || [];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 1 }}
      className="h-[400px]"
    >
      <ResponsiveContainer>
        <LineChart
          data={chartData}
          margin={{ top: 20, right: 20, left: 0, bottom: 20 }}
        >
          <XAxis
            dataKey="year"
            type="category"
            tick={{ fontSize: 12, fill: "#6B7280" }}
            interval={0}
          />
          <YAxis
            tick={{ fontSize: 12, fill: "#6B7280" }}
            tickFormatter={(value) => `${value}%`}
          />
          <Tooltip />
          {trendsData.map((trend, idx) => (
            <Line
              key={trend.name}
              type="monotone"
              dataKey={trend.name}
              name={trend.name}
              stroke={colors[idx % colors.length]}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 6 }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </motion.div>
  );
};

const CustomTooltip = ({ active, payload, label }: CustomTooltipProps) => {
  if (active && payload && payload.length) {
    const data = payload[0];
    return (
      <div className="bg-white p-3 rounded-lg shadow-gray-200 border border-gray-100">
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 rounded-full" style={{ backgroundColor: data.stroke }} />
          <span className="font-medium text-sm text-gray-900">{data.name}</span>
        </div>
        <p className="text-sm text-gray-600 mt-1">{label}: {data.value}%</p>
      </div>
    );
  }
  return null;
};

type YCCompanyInfo = { name: string; logo: string };
type YCTrends = "Privacy-Preserving AI" | "Explainable AI" | "Personalized Finance" | "AI-Powered Decision Support" | "Real-Time Forecasting" | "AI Ethics" | "Hyperautomation" | "Data Democratization" | "AI Regulation" | "Fintech";
const ycCompanies: Record<YCTrends, readonly YCCompanyInfo[]> = {
  "Privacy-Preserving AI": [
    { name: "Neuralink", logo: "/company-logos/neuralink.png" },
    { name: "Kernel", logo: "/company-logos/kernel.png" },
  ],
  "Explainable AI": [
    { name: "Magic Leap", logo: "/company-logos/magic-leap.png" },
    { name: "Mojo Vision", logo: "/company-logos/mojo-vision.png" },
  ],
  "Personalized Finance": [
    { name: "Plaid", logo: "/company-logos/plaid.png" },
    { name: "Stripe", logo: "/company-logos/stripe.png" },
  ],
  "AI-Powered Decision Support": [
    { name: "Salesforce", logo: "/company-logos/salesforce.png" },
    { name: "Tableau", logo: "/company-logos/tableau.png" },
  ],
  "Real-Time Forecasting": [
    { name: "Meteor", logo: "/company-logos/meteor.png" },
    { name: "Forecasta", logo: "/company-logos/forecasta.png" },
  ],
  "AI Ethics": [
    { name: "DeepMind", logo: "/company-logos/deepmind.png" },
    { name: "OpenAI", logo: "/company-logos/openai.png" },
  ],
  "Hyperautomation": [
    { name: "UiPath", logo: "/company-logos/uipath.png" },
    { name: "Automation Anywhere", logo: "/company-logos/automation-anywhere.png" },
  ],
  "Data Democratization": [
    { name: "Snowflake", logo: "/company-logos/snowflake.png" },
    { name: "Databricks", logo: "/company-logos/databricks.png" },
  ],
  "AI Regulation": [
    { name: "Regtech Solutions", logo: "/company-logos/regtech.png" },
    { name: "ComplianceAI", logo: "/company-logos/complianceai.png" },
  ],
  "Fintech": [
    { name: "Square", logo: "/company-logos/square.png" },
    { name: "PayPal", logo: "/company-logos/paypal.png" },
  ],
} as const;

const CompanyLogo = ({ src, name }: { src: string; name: string }) => {
  const [error, setError] = useState(false);
  const initials = name.split(" ").map((word) => word[0]).join("").toUpperCase().slice(0, 2);
  if (error) return <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center"><span className="text-xs font-medium text-blue-600">{initials}</span></div>;
  return (
    <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center overflow-hidden">
      <img src={src} alt={`${name} logo`} className="w-full h-full object-cover" onError={() => setError(true)} />
    </div>
  );
};

export default function Home() {
  const [initialTrendsData, setInitialTrendsData] = useState<any[]>(starterTrends);
  const [trendsData, setTrendsData] = useState<ProcessedRow[]>([]);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [selectedTrend, setSelectedTrend] = useState<ProcessedRow | null>(null);
  const [filteredData, setFilteredData] = useState<ProcessedRow[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [currentStep, setCurrentStep] = useState<string>("");
  const [stepQueue, setStepQueue] = useState<string[]>([]);
  const [isStepLoading, setIsStepLoading] = useState(false);
  const [isLegendOpen, setIsLegendOpen] = useState(false);
  const [isDetailsOpen, setIsDetailsOpen] = useState(false);

  const processStepQueue = async () => {
    if (stepQueue.length > 0 && !isStepLoading) {
      setIsStepLoading(true);
      setCurrentStep(stepQueue[0]);
      await new Promise(resolve => setTimeout(resolve, 800));
      setStepQueue(prev => prev.slice(1));
      setIsStepLoading(false);
    }
  };

  useEffect(() => {
    processStepQueue();
  }, [stepQueue]);

  const fetchTrends = async (query: string) => {
    setIsLoading(true);
    setError(null);
    setStepQueue(prev => [...prev, `Starting exploration for "${query}"…`]);
    console.log("Starting fetchTrends for query:", query);

    setStepQueue(prev => [...prev, "Building request payload…"]);
    const requestBody = JSON.stringify({
      user_input: query,
      focus_area: "business_opportunities",
      k: 10,
    });
    console.log("Request payload:", requestBody);

    const requestHeaders = {
      "Accept": "application/json",
      "Content-Type": "application/json",
      "Origin": window.location.origin,
    };

    setStepQueue(prev => [...prev, "Sending API request…"]);
    console.log("Sending API request to:", "https://simple-lobster-morally.ngrok-free.app/analyze");
    try {
      const response = await fetch("https://simple-lobster-morally.ngrok-free.app/analyze", {
        method: "POST",
        headers: requestHeaders,
        credentials: "omit",
        body: requestBody,
      });

      console.log("API response status:", response.status);
      if (!response.ok) {
        setStepQueue(prev => [...prev, `API error: ${response.status} - ${response.statusText}`]);
        throw new Error(`HTTP error! status: ${response.status} - ${response.statusText}`);
      }

      setStepQueue(prev => [...prev, "Parsing API response…"]);
      const data = await response.json();
      console.log("Raw API response:", data);

      setStepQueue(prev => [...prev, "Validating data format…"]);
      // Updated to match new API response structure: { "status": "success", "data": { "final_result": { "trends": [...] } } }
      if (!data.data || !data.data.final_result || !Array.isArray(data.data.final_result.trends)) {
        setStepQueue(prev => [...prev, "Invalid data format detected"]);
        console.error("Invalid API response format:", data);
        setError("No trends found for this query or API returned invalid data");
        setTrendsData([]);
        setFilteredData([]);
        setIsLoading(false);
        return;
      }

      setStepQueue(prev => [...prev, `Processing ${data.data.final_result.trends.length} trends…`]);
      const processedTrends = data.data.final_result.trends.map((trend: any) => {
        const mappedTrend = {
          Trend: trend.name || "Unknown Trend",
          "Startup Opportunity": trend.Startup_Opportunity || trend.description || "Unknown Opportunity",
          "Related Trends": trend.Related_trends || "",
          "Growth Rate, WoW": trend.Growth_rate_WoW || 0,
          "YC Chances": trend.YC_chances < 1 ? trend.YC_chances * 100 : trend.YC_chances || 0,
          "2025": trend.Year_2025 || 0,
          "2026": trend.Year_2026 || 0,
          "2027": trend.Year_2027 || 0,
          "2028": trend.Year_2028 || 0,
          "2029": trend.Year_2029 || 0,
          "2030": trend.Year_2030 || 0,
        };
        setStepQueue(prev => [...prev, `Mapping trend: "${mappedTrend.Trend}"…`]);
        console.log("Mapped trend:", mappedTrend);
        return mappedTrend as ProcessedRow;
      });
      console.log("Processed trends array:", processedTrends);

      setStepQueue(prev => [...prev, "Updating trends data…"]);
      const sortedTrends = processedTrends.sort((a: ProcessedRow, b: ProcessedRow) => b["Growth Rate, WoW"] - a["Growth Rate, WoW"]);
      setTrendsData(sortedTrends);
      setFilteredData(sortedTrends);
      console.log("Updated trendsData (sorted):", sortedTrends);
      console.log("Updated filteredData (sorted):", sortedTrends);

      if (sortedTrends.length > 0) {
        setStepQueue(prev => [...prev, `Selecting first trend: "${sortedTrends[0].Trend}"…`]);
        setSelectedTrend(sortedTrends[0]);
        console.log("Selected first trend:", sortedTrends[0]);
      } else {
        setStepQueue(prev => [...prev, "No trends returned by API"]);
        console.log("No trends returned by API");
      }

      setStepQueue(prev => [...prev, "Preparing results…"]);
      await new Promise(resolve => setTimeout(resolve, 1000));
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : "Failed to fetch trends from API";
      setError(errorMessage);
      console.error("Error during fetchTrends:", errorMessage);
      setTrendsData([]);
      setFilteredData([]);
    } finally {
      setIsLoading(false);
      console.log("fetchTrends complete. Final trendsData:", trendsData);
    }
  };

  const pivotedData = years.map((year) => {
    const obj: { year: string; [key: string]: number | string } = { year };
    filteredData.forEach((row) => { obj[row.Trend] = row[year as keyof ProcessedRow]; });
    return obj;
  });

  const handleMouseMove = (state: any) => {
    if (state?.activePayload?.[0]) {
      const trendName = state.activePayload[0].dataKey;
      const selected = filteredData.find((row) => row.Trend === trendName);
      if (selected) setSelectedTrend(selected);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="h-auto bg-white shadow-sm border-b sticky top-0 z-50 py-2">
        <div className="max-w-[1920px] mx-auto px-4">
          <div className="flex items-center justify-start h-16">
            <div className="flex items-center space-x-2">
              <Sparkles className="h-6 w-6 text-gray-700" />
              <h1 className="text-xl font-semibold text-gray-900">SpyGlass Trends</h1>
            </div>
          </div>
        </div>
      </header>

      {!hasSearched ? (
        <div className="flex flex-col items-center custom-min-height px-4 py-6 bg-gradient-to-b from-gray-50 to-gray-200">
          <div className="w-full max-w-4xl flex-1 flex flex-col justify-between pb-0">  
            <div>
              <div className="relative h-[300px] sm:h-[400px]" aria-label="Interactive trend chart">
                <TrendChart trendsData={initialTrendsData} />
                <div className="absolute top-4 left-4 text-white bg-gray-800 bg-opacity-50 px-2 py-1 rounded-2xl">
                  <p className="text-sm">Trending Growth Rates (Hover for Details)</p>
                </div>
              </div>
              <div className="text-center space-y-8">
                <h2 className="text-3xl font-semibold text-gray-900">Discover Trending Opportunities</h2>
                <p className="text-lg text-gray-700">Explore key trends or search your own!</p>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 max-w-2xl mx-auto">
                  {starterQueries.map((query) => (
                    <Button
                      key={query}
                      variant="outline"
                      className="h-auto py-3 text-base text-gray-700 hover:bg-gray-100"
                      onClick={() => {
                        setSearchQuery(query);
                        setHasSearched(true);
                        fetchTrends(query);
                      }}
                    >
                      {query}
                    </Button>
                  ))}
                </div>
              </div>
            </div>
            <SearchInput
              onSearch={(query) => {
                setSearchQuery(query);
                setHasSearched(true);
                fetchTrends(query);
              }}
              placeholder="Search trends..."
              className="SearchInput !mb-1"
              value={searchQuery}
            />
          </div>
        </div>
      ) : isLoading ? (
        <div className="flex flex-col items-center custom-min-height px-4 pt-6 pb-2 bg-gradient-to-b from-gray-50 to-gray-200">
          <div className="w-full max-w-4xl flex-1 flex flex-col justify-center items-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="text-center space-y-6 p-6 bg-white bg-opacity-10 backdrop-blur-lg rounded-2xl shadow-md border border-gray-200"
            >
              <div className="space-y-4 max-h-[40vh] overflow-y-auto">
                {stepQueue.map((step, index) => (
                  <motion.p
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                    className={cn(
                      "text-lg text-gray-700 italic",
                      index === stepQueue.length - 1 && isStepLoading ? "loading-dots animate-fade-in" : "opacity-70"
                    )}
                  >
                    {index === stepQueue.length - 1 && isStepLoading
                      ? `${step} (In Progress)`
                      : step + (index < stepQueue.length - 1 ? " ✓" : "")}
                  </motion.p>
                ))}
              </div>
              <progress
                value={(stepQueue.length - (isStepLoading ? 1 : 0)) * 20}
                max="100"
                className="w-full h-2 bg-gray-200 rounded-full overflow-hidden"
              >
                {Math.min((stepQueue.length - (isStepLoading ? 1 : 0)) * 20, 100)}%
              </progress>
              <div className="flex items-center justify-center gap-2">
                <span className="text-sm text-gray-500">
                  Progress: {Math.min((stepQueue.length - (isStepLoading ? 1 : 0)) * 20, 100)}%
                </span>
                {isLoading && (
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
                    className="w-4 h-4 border-4 border-t-[transparent] border-[conic-gradient(from 90deg, #6366f1, #ec4899, #06b6d4, #f59e0b, #10b981, #8b5cf6)] rounded-full"
                  />
                )}
              </div>
            </motion.div>
          </div>
          <SearchInput
            onSearch={(query) => {
              setSearchQuery(query);
              setHasSearched(true);
              fetchTrends(query);
            }}
            placeholder="Search trends..."
            className="SearchInput !mb-1"
            value={searchQuery}
          />
        </div>
      ) : error ? (
        <div className="flex flex-col items-center custom-min-height px-4 pt-6 pb-2 bg-gradient-to-b from-gray-50 to-gray-200">
          <div className="w-full max-w-4xl flex-1 flex flex-col justify-between pb-0">
            <div className="text-center text-red-600 p-4 rounded-lg">
              <h3 className="text-lg font-semibold mb-2">Error Loading Data</h3>
              <p>{error}</p>
              {currentStep && (
                <div className="mt-4 text-sm text-gray-600">
                  <p>Last step: {currentStep}</p>
                </div>
              )}
              <Button onClick={() => fetchTrends(searchQuery)} className="mt-4 px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-800">
                Try Again
              </Button>
            </div>
            <SearchInput
              onSearch={(query) => {
                setSearchQuery(query);
                setHasSearched(true);
                fetchTrends(query);
              }}
              placeholder="Search trends..."
              className="SearchInput !mb-1"
              value={searchQuery}
            />
          </div>
        </div>
      ) : (
        <motion.main
          className="px-2 py-4 custom-min-height overflow-y-auto" 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          <div className="flex flex-col md:flex-row gap-4 max-w-[1920px] mx-auto h-full">
            <div className="w-full md:w-72 shrink-0 md:sticky md:top-0"> 
              <Card className="md:h-[calc(100vh-64px)] bg-white shadow-gray-200 overflow-y-auto">
                <CardHeader className="flex justify-between items-center sticky top-0 bg-white z-10"> 
                  <CardTitle className="text-sm font-medium text-gray-500">Trend Categories</CardTitle>
                  <Button variant="ghost" className="md:hidden" onClick={() => setIsLegendOpen(!isLegendOpen)}>
                    {isLegendOpen ? "Hide" : "Show"}
                  </Button>
                </CardHeader>
                <CardContent className={`${isLegendOpen ? "block" : "hidden"} md:block space-y-3`}>
                  {filteredData.length > 0 ? (
                    filteredData.map((trend, idx) => (
                      <div key={trend.Trend} className="flex items-start space-x-2.5 px-2 py-1.5 rounded-md hover:bg-gray-50">
                        <div className="w-2.5 h-2.5 rounded-full mt-1.5 shrink-0" style={{ backgroundColor: colors[idx % colors.length] }} />
                        <span className="text-sm text-gray-700 break-words overflow-wrap-anywhere leading-tight">{trend.Trend}</span>
                      </div>
                    ))
                  ) : (
                    <div className="text-sm text-gray-500">No trends available</div>
                  )}
                </CardContent>
              </Card>
            </div>

            <div className="flex-1 flex flex-col gap-4">
              <Card className="bg-white shadow-gray-200 md:sticky md:top-0 z-10">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-xl font-semibold text-gray-900">Technology Adoption Trends</CardTitle>
                    <Select defaultValue="5y">
                      <SelectTrigger className="w-32"><SelectValue placeholder="Time Range" /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="5y">5 Years</SelectItem>
                        <SelectItem value="3y">3 Years</SelectItem>
                        <SelectItem value="1y">1 Year</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="h-[250px] sm:h-[300px] md:h-[400px] w-full">
                    {filteredData.length > 0 ? (
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={pivotedData} onMouseMove={handleMouseMove} margin={{ top: 10, right: 10, left: 0, bottom: 10 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" opacity={0.4} />
                          <XAxis dataKey="year" tick={{ fontSize: 12, fill: "#6B7280" }} tickLine={false} axisLine={{ stroke: "#E2E8F0" }}>
                            <Label value="Timeline (Years)" position="bottom" style={{ fill: "#6B7280", fontSize: 12 }} />
                          </XAxis>
                          <YAxis domain={[0, 100]} tickLine={false} axisLine={{ stroke: "#E2E8F0" }} tick={{ fontSize: 12, fill: "#6B7280" }} tickFormatter={(value) => `${value}%`}>
                            <Label value="Market Adoption (%)" angle={-90} position="left" style={{ fill: "#6B7280", fontSize: 12 }} />
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
                              activeDot={{ r: 6, fill: colors[idx % colors.length], stroke: "white", strokeWidth: 2 }}
                              opacity={selectedTrend ? (selectedTrend.Trend === trend.Trend ? 1 : 0.2) : 1}
                            />
                          ))}
                        </LineChart>
                      </ResponsiveContainer>
                    ) : (
                      <div className="flex items-center justify-center h-full text-gray-500">No data available to display</div>
                    )}
                  </div>
                </CardContent>
              </Card>

              <div className="overflow-y-auto md:h-[calc(100vh-64px-16px-400px)]"> 
                {filteredData.length > 0 ? (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pb-4">
                    {filteredData.map((trend, idx) => (
                      <motion.div key={trend.Trend} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: idx * 0.1 }}>
                        <Card
                          className={`cursor-pointer transition-all hover:shadow-lg bg-white shadow-md border border-gray-200 rounded-lg ${selectedTrend?.Trend === trend.Trend ? "ring-2 ring-gray-500" : ""}`}
                          onClick={() => setSelectedTrend(trend)}
                          onMouseEnter={() => setSelectedTrend(trend)}
                        >
                          <CardContent className="p-4">
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <h3 className="font-semibold text-gray-900">{trend["Startup Opportunity"]}</h3>
                                <p className="text-sm text-gray-500 mt-1">{trend.Trend}</p>
                              </div>
                              <Badge className="bg-gray-200 text-gray-700 flex items-center space-x-1 ml-2 shrink-0">
                                <TrendingUp className="h-3 w-3" /><span>{trend["Growth Rate, WoW"]} % WoW</span>
                              </Badge>
                            </div>
                          </CardContent>
                        </Card>
                      </motion.div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center text-gray-500 py-4">No trends to display</div>
                )}
              </div>
            </div>

            <div className="w-full md:w-80 shrink-0 md:sticky md:top-0"> 
              <Card className="md:h-[calc(100vh-64px)] bg-white shadow-gray-200 overflow-y-auto"> 
                <CardHeader className="flex justify-between items-center sticky top-0 bg-white z-10"> 
                  <CardTitle className="text-gray-900">Trend Details</CardTitle>
                  <Button variant="ghost" className="md:hidden" onClick={() => setIsDetailsOpen(!isDetailsOpen)}>
                    {isDetailsOpen ? "Hide" : "Show"}
                  </Button>
                </CardHeader>
                <CardContent className={`${isDetailsOpen ? "block" : "hidden"} md:block`}>
                  {selectedTrend ? (
                    <div className="space-y-6">
                      <div>
                        <h2 className="text-xl font-semibold text-gray-900">{selectedTrend.Trend}</h2>
                        <p className="mt-2 text-gray-500">{selectedTrend["Startup Opportunity"]}</p>
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <Card className="bg-indigo-50">
                          <CardContent className="p-4">
                            <div className="flex items-center space-x-2">
                              <TrendingUp className="h-4 w-4 text-indigo-600" />
                              <div>
                                <p className="text-sm text-gray-500">Growth Rate, WoW</p>
                                <p className="font-semibold text-gray-900">{selectedTrend["Growth Rate, WoW"]}%</p>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                        <Card className="bg-indigo-50">
                          <CardContent className="p-4">
                            <div className="flex items-center space-x-2">
                              <Zap className="h-4 w-4 text-indigo-600" />
                              <div>
                                <p className="text-sm text-gray-500">YC Acceptance Probability</p>
                                <p className="font-semibold text-gray-900">{selectedTrend["YC Chances"].toFixed(1)}%</p>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      </div>
                      <div>
                        <h3 className="font-medium text-gray-900 mb-2">Related Trends</h3>
                        <div className="flex flex-wrap gap-2">
                          {selectedTrend["Related Trends"].split(",").map((trend) => (
                            <Badge key={trend.trim()} className="bg-indigo-50 text-indigo-700">{trend.trim()}</Badge>
                          ))}
                        </div>
                      </div>
                      <div>
                        <h3 className="font-medium text-gray-900 mb-2">YC-Funded Companies</h3>
                        <div className="flex flex-col space-y-2">
                          {selectedTrend && ycCompanies[selectedTrend.Trend as YCTrends]?.map((company) => (
                            <div key={company.name} className="flex items-center p-2 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-colors">
                              <CompanyLogo src={company.logo} name={company.name} />
                              <span className="ml-3 text-sm font-medium text-gray-900">{company.name}</span>
                            </div>
                          ))}
                          {selectedTrend && !ycCompanies[selectedTrend.Trend as YCTrends] && (
                            <div className="text-sm text-gray-500">No YC companies found for this trend</div>
                          )}
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="flex items-center justify-center h-full text-gray-500">Select a trend to view details</div>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
          <div className="fixed bottom-0 left-0 right-0 p-2 sm:p-4 border-t shadow-lg z-50">
            <div className="max-w-[1920px] mx-auto flex justify-center">
              <div className="w-full max-w-4xl px-2 sm:px-0">
                <SearchInput
                  onSearch={(query) => {
                    setSearchQuery(query);
                    setHasSearched(true);
                    fetchTrends(query);
                  }}
                  placeholder="Search trends..."
                  className="SearchInput !mb-1"
                  value={searchQuery}
                />
              </div>
            </div>
          </div>
        </motion.main>
      )}
    </div>
  );
}