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
  Legend,
Label  // Add this
} from "recharts";
import { Search, Sparkles, TrendingUp, Zap, Download } from "lucide-react";
import { motion } from "framer-motion";

// Import necessary shadcn components
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

import { useTheme } from "next-themes"
import { Moon, Sun } from "lucide-react"

interface Trend {
  name: string;
  description: string;
  Startup_Opportunity: string;
  Startup_Name: string;
  Related_trends: string;
  Growth_rate_WoW: number;
  YC_chances: number;
  Year_2025: number;
  Year_2026: number;
  Year_2027: number;
  Year_2028: number;
  Year_2029: number;
  Year_2030: number;
}

interface ApiResponse {
  trends: Trend[];
}

const years = ["Year_2025", "Year_2026", "Year_2027", "Year_2028", "Year_2029", "Year_2030"];

export default function Home() {
  const [trendsData, setTrendsData] = useState<Trend[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedTrend, setSelectedTrend] = useState<Trend | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
const [filteredData, setFilteredData] = useState<Trend[]>([]);

  const { theme, setTheme } = useTheme();

  const fetchTrends = async () => {
    setIsLoading(true);
    try {
      console.log('Sending request to API...');
      const response = await fetch('https://simple-lobster-morally.ngrok-free.app/analyze', {
        method: 'POST',
        headers: {
          'accept': 'application/json',
          'Content-Type': 'application/json',
          'ngrok-skip-browser-warning': 'true'
        },
        mode: 'cors',
        body: JSON.stringify({
          user_input: searchQuery || "new uses for ai",
          focus_area: "business_opportunities",
          k: 5
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      console.log('Response received, parsing JSON...');
      const data = await response.json();
      console.log('Raw API Response:', data);
      
      // Log the structure of the data
      console.log('Data type:', typeof data);
      console.log('Has trends property:', 'trends' in data);
      if ('trends' in data) {
        console.log('Trends type:', typeof data.trends);
        console.log('Is trends an array:', Array.isArray(data.trends));
        if (Array.isArray(data.trends) && data.trends.length > 0) {
          console.log('First trend object:', data.trends[0]);
        }
      }

      // Ensure the data matches our expected format
      if (data.trends && Array.isArray(data.trends)) {
        console.log('Setting trend data with', data.trends.length, 'trends');
        setTrendsData(data.trends);
        setFilteredData(data.trends);
        if (data.trends.length > 0) {
          console.log('Setting selected trend:', data.trends[0]);
          setSelectedTrend(data.trends[0]);
        }
      } else {
        throw new Error('Invalid data format received from API');
      }
    } catch (error) { 
      console.error('Error fetching trends:', error);
      // Set some default data or show an error state
      setTrendsData([]);
      // setFilteredData([]);
    } finally {
      setIsLoading(false);
    }
  };

  // Add debounce to prevent too many API calls
  useEffect(() => {
    const timer = setTimeout(() => {
      fetchTrends();
    }, 500); // Wait 500ms after the user stops typing

    return () => clearTimeout(timer);
  }, [searchQuery]);


  useEffect(() => {
    // const filtered = trendsData.filter((trend) =>
    //   trend.name.toLowerCase().includes(searchQuery.toLowerCase())
    // );
    setFilteredData(trendsData);
  }, [searchQuery, trendsData]);

  const pivotedData = years.map((year) => {
    console.log('Pivoting data for', year);
    const obj: { year: string; [key: string]: number | string } = { 
      year: year.replace('Year_', '')
    };
    console.log('Pivoting', filteredData.length, 'filtered trends');
    filteredData.forEach((trend) => {
      obj[trend.name] = trend[year];
      console.log(`Pivoting trend ${trend.name} for year ${year}`);
    });
    return obj;
  });

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

  const getColor = (trend: string, idx: number) => colors[idx % colors.length];

  const handleMouseMove = (state: any) => {
    if (state && state.activePayload && state.activePayload.length > 0) {
      const trendName = state.activePayload[0].dataKey;
      const selected = trendsData.find((trend) => trend.name === trendName);
      if (selected) setSelectedTrend(selected);
    }
  };


  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0]; // Only show data for the hovered line
      return (
        <Card className="border-none shadow-lg">
          <CardContent className="p-3">
            <div className="flex items-center space-x-2">
              <div
                className="w-2 h-2 rounded-full"
                style={{ backgroundColor: data.color }}
              />
              <div>
                <p className="text-sm font-medium">{data.name}</p>
                <p className="text-sm text-muted-foreground">
                  {label}: {(data.value * 100).toFixed(1)}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      );
    }
    return null;
  };

return (
  <div className="min-h-screen bg-background">
    {/* Header */}
    <header className="bg-background/80 backdrop-blur-lg border-b sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-2">
            <Sparkles className="h-6 w-6 text-indigo-600 dark:text-indigo-400" />
            <h1 className="text-xl font-semibold text-foreground">
              SpyGlass Trends
            </h1>
          </div>
          <div className="flex items-center space-x-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                type="text"
                placeholder="Search trends..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 w-64"
              />
            </div>
            <Button variant="default">
              <Sparkles className="h-4 w-4 mr-2" />
              Generate Report
            </Button>
          </div>
        </div>
      </div>
    </header>

    {/* Main Content */}
    <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex gap-6">
        {/* Left Legend */}
        <div className="w-48 pt-24">
          <div className="sticky top-24 space-y-4">
            {filteredData.map((trend, idx) => (
              <div
                key={trend.name}
                className="flex items-center space-x-2.5 group cursor-pointer"
                onMouseEnter={() => setSelectedTrend(trend)}
              >
                <div className="relative">
                  <div
                    className="w-2.5 h-2.5 rounded-full"
                    style={{ backgroundColor: colors[idx % colors.length] }}
                  />
                  <div
                    className="absolute -inset-2 rounded-full opacity-0 group-hover:opacity-20 transition-opacity"
                    style={{ backgroundColor: colors[idx % colors.length] }}
                  />
                </div>
                <span className="text-sm text-muted-foreground whitespace-nowrap transition-colors group-hover:text-foreground">
                  {trend.name}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Main Content Area */}
        <div className="flex-1 space-y-6">
          {/* Chart Card */}
          <Card className="overflow-hidden relative">
            {isLoading && (
              <div className="absolute inset-0 bg-background/50 backdrop-blur-sm flex items-center justify-center z-50">
                <div className="animate-spin rounded-full h-8 w-8 border-4 border-primary border-t-transparent"></div>
              </div>
            )}
            <CardHeader className="space-y-1">
              <div className="flex items-center justify-between">
                <CardTitle className="text-xl font-semibold">
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
              <div className="h-[600px]">
                <ResponsiveContainer>
                  <LineChart
                    data={pivotedData}
                    onMouseMove={handleMouseMove}
                    margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
                  >
                    <CartesianGrid 
                      strokeDasharray="3 3" 
                      stroke="currentColor" 
                      className="stroke-border/30" 
                    />
                    <XAxis
                      dataKey="year"
                      tick={{ fontSize: 12 }}
                      tickLine={false}
                      axisLine={{ stroke: 'currentColor' }}
                      className="text-muted-foreground"
                    >
                      <Label
                        value="Timeline (Years)"
                        position="bottom"
                        className="text-muted-foreground"
                      />
                    </XAxis>
                    <YAxis
                      domain={[0, 100]}
                      tickLine={false}
                      axisLine={{ stroke: 'currentColor' }}
                      tick={{ fontSize: 12 }}
                      className="text-muted-foreground"
                      tickFormatter={(value) => `${value}%`}
                    >
                      <Label
                        value="Market Adoption (%)"
                        angle={-90}
                        position="left"
                        className="text-muted-foreground"
                      />
                    </YAxis>
                    <Tooltip
                      content={<CustomTooltip />}
                      cursor={{ stroke: 'currentColor', strokeWidth: 1, strokeDasharray: '4 4' }}
                    />
                    {filteredData.map((trend, idx) => (
                      <Line
                        key={trend.name}
                        type="monotone"
                        dataKey={trend.name}
                        stroke={colors[idx % colors.length]}
                        strokeWidth={2}
                        dot={false}
                        activeDot={{
                          r: 6,
                          fill: colors[idx % colors.length],
                          stroke: 'white',
                          strokeWidth: 2,
                        }}
                      />
                    ))}
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          {/* Opportunities List */}
          <div className="grid grid-cols-2 gap-4">
            {filteredData.map((trend, idx) => (
              <motion.div
                key={`${trend.name}-${trend.Startup_Name}`}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.1 }}
              >
                <Card
                  className={`cursor-pointer transition-all hover:shadow-lg ${
                    selectedTrend?.name === trend.name ? "ring-2 ring-primary" : ""
                  }`}
                  onClick={() => setSelectedTrend(trend)}
                >
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                      <div>
                        <h3 className="font-semibold text-foreground">
                          {trend.Startup_Name}
                        </h3>
                        <p className="text-sm text-muted-foreground mt-1">
                          {trend.Startup_Opportunity}
                        </p>
                      </div>
                      <Badge
                        variant="secondary"
                        className="flex items-center space-x-1"
                      >
                        <TrendingUp className="h-3 w-3" />
                        <span>{trend.Growth_rate_WoW}</span>
                      </Badge>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Right Details Panel */}
        <div className="w-80">
          <div className="sticky top-24">
            <Card>
              <CardHeader>
                <CardTitle>Opportunity Details</CardTitle>
              </CardHeader>
              <CardContent>
                {selectedTrend ? (
                  <div className="space-y-6">
                    <div>
                      <h2 className="text-xl font-semibold text-foreground">
                        {selectedTrend.Startup_Name}
                      </h2>
                      <p className="mt-2 text-muted-foreground">
                        {selectedTrend.Startup_Opportunity}
                      </p>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <Card>
                        <CardContent className="p-4">
                          <div className="flex items-center space-x-2">
                            <TrendingUp className="h-4 w-4 text-green-500" />
                            <div>
                              <p className="text-sm text-muted-foreground">Growth Rate</p>
                              <p className="font-semibold">
                                {selectedTrend.Growth_rate_WoW}
                              </p>
                            </div>
                          </div>
                        </CardContent>
                      </Card>

                      <Card>
                        <CardContent className="p-4">
                          <div className="flex items-center space-x-2">
                            <Zap className="h-4 w-4 text-yellow-500" />
                            <div>
                              <p className="text-sm text-muted-foreground">YC Chances</p>
                              <p className="font-semibold">
                                {selectedTrend.YC_chances}
                              </p>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    </div>

                    <div>
                      <h3 className="font-medium text-foreground mb-2">
                        Related Trends
                      </h3>
                      <div className="flex flex-wrap gap-2">
                        {selectedTrend.Related_trends
                          ?.split(",")
                          .map((trend) => (
                            <Badge
                              key={trend.trim()}
                              variant="secondary"
                              className="text-sm"
                            >
                              {trend.trim()}
                            </Badge>
                          ))}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="flex items-center justify-center h-full text-muted-foreground">
                    Select a trend to view details
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </main>
  </div>
);