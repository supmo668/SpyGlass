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
import Papa from "papaparse";
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

interface CSVRow {
  Trend: string;
  "Startup Opportunity": string;
  "Related trends": string;
  "Growth rate, WoW": string;
  "YC chances": string;
  "2025": string;
  "2026": string;
  "2027": string;
  "2028": string;
  "2029": string;
  "2030": string;
}

interface ProcessedRow
  extends Omit<
    CSVRow,
    "2025" | "2026" | "2027" | "2028" | "2029" | "2030"
  > {
  "2025": number;
  "2026": number;
  "2027": number;
  "2028": number;
  "2029": number;
  "2030": number;
}

const years = ["2025", "2026", "2027", "2028", "2029", "2030"];

export default function Home() {
  const [csvData, setCsvData] = useState<ProcessedRow[]>([]);
  const [selectedTrend, setSelectedTrend] = useState<ProcessedRow | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [filteredData, setFilteredData] = useState<ProcessedRow[]>([]);

  const { theme, setTheme } = useTheme();

  useEffect(() => {
    fetch("/Gemini Advanced 20 Pro Experimental.csv")
      .then((res) => res.text())
      .then((csvText) => {
        Papa.parse(csvText, {
          header: true,
          skipEmptyLines: true,
          complete: (results) => {
            const processed: ProcessedRow[] = results.data.map((row: CSVRow) => {
              const newRow = { ...row } as ProcessedRow;
              years.forEach((year) => {
                newRow[year] = parseFloat(newRow[year]?.replace("%", "") || "0");
              });
              return newRow;
            });
            setCsvData(processed);
            setFilteredData(processed);
          },
        });
      });
  }, []);

  useEffect(() => {
    const filtered = csvData.filter((row) =>
      row.Trend.toLowerCase().includes(searchQuery.toLowerCase())
    );
    setFilteredData(filtered);
  }, [searchQuery, csvData]);

  const pivotedData = years.map((year) => {
    const obj: { year: string; [key: string]: number | string } = { year };
    filteredData.forEach((row) => {
      obj[row.Trend] = row[year];
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
      const selected = csvData.find((row) => row.Trend === trendName);
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
                  {label}: {data.value}%
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
              <Download className="h-4 w-4 mr-2" />
              Export Report
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
                key={trend.Trend}
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
                  {trend.Trend}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Main Content Area */}
        <div className="flex-1 space-y-6">
          {/* Chart Card */}
          <Card className="overflow-hidden">
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
                        key={trend.Trend}
                        type="monotone"
                        dataKey={trend.Trend}
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
                key={trend.Trend}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.1 }}
              >
                <Card
                  className={`cursor-pointer transition-all hover:shadow-lg ${
                    selectedTrend?.Trend === trend.Trend ? "ring-2 ring-primary" : ""
                  }`}
                  onClick={() => setSelectedTrend(trend)}
                >
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                      <div>
                        <h3 className="font-semibold text-foreground">
                          {trend.Trend}
                        </h3>
                        <p className="text-sm text-muted-foreground mt-1">
                          {trend["Startup Opportunity"]}
                        </p>
                      </div>
                      <Badge
                        variant="secondary"
                        className="flex items-center space-x-1"
                      >
                        <TrendingUp className="h-3 w-3" />
                        <span>{trend["Growth rate, WoW"]}</span>
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
                <CardTitle>Trend Details</CardTitle>
              </CardHeader>
              <CardContent>
                {selectedTrend ? (
                  <div className="space-y-6">
                    <div>
                      <h2 className="text-xl font-semibold text-foreground">
                        {selectedTrend.Trend}
                      </h2>
                      <p className="mt-2 text-muted-foreground">
                        {selectedTrend["Startup Opportunity"]}
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
                                {selectedTrend["Growth rate, WoW"]}
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
                                {selectedTrend["YC chances"]}
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
                        {selectedTrend["Related trends"]
                          .split(",")
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