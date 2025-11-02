import { GoogleGenAI, Type } from "@google/genai";
import { Route, RoutePreferences, Preference, TransportMode } from '../types';

if (!process.env.API_KEY) {
    throw new Error("API_KEY environment variable not set");
}

const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

const routeSchema = {
  type: Type.ARRAY,
  items: {
    type: Type.OBJECT,
    properties: {
      id: { type: Type.STRING, description: 'A unique identifier for the route, e.g., route-1' },
      routeName: { type: Type.STRING, description: 'A descriptive name for the route, e.g., "Metro Express via Blue Line"' },
      totalDuration: { type: Type.INTEGER, description: 'Total journey time in minutes.' },
      totalCost: { type: Type.NUMBER, description: 'Estimated total cost in Indian Rupees (INR). A cheap fare is under 30 INR.' },
      comfortScore: { type: Type.INTEGER, description: 'A score from 1 (very crowded, many transfers) to 10 (spacious, few transfers).' },
      confidenceScore: { type: Type.NUMBER, description: 'AI confidence in this route suggestion, from 0.0 to 1.0.' },
      summary: { type: Type.STRING, description: 'A brief 1-2 sentence summary of the route highlighting its main benefit (e.g., fastest, avoids traffic).' },
      realtimeInfo: { type: Type.STRING, description: 'Optional. A top-level alert about real-time conditions for this route, e.g., "Minor metro delays expected".' },
      segments: {
        type: Type.ARRAY,
        items: {
          type: Type.OBJECT,
          properties: {
            mode: { type: Type.STRING, enum: Object.values(TransportMode), description: 'Mode of transport for this segment.' },
            details: { type: Type.STRING, description: 'Specifics of the segment, like bus number, metro line, or walking directions.' },
            duration: { type: Type.INTEGER, description: 'Duration of this segment in minutes.' },
            distance: { type: Type.NUMBER, description: 'Distance of this segment in kilometers. Optional.' },
            stops: { type: Type.INTEGER, description: 'Number of stops in this transit segment. Optional.' },
            realtimeInfo: { type: Type.STRING, description: 'Optional. An alert for this specific segment, e.g., "Bus is running 15 mins late".' },
            path: {
              type: Type.ARRAY,
              description: "An array of {lat, lng} coordinates representing the path for this segment. Required for BUS and METRO modes to draw on the map. Provide a simplified path of 5-10 points. For WALK/AUTO_RICKSHAW, this can be an empty array.",
              items: {
                type: Type.OBJECT,
                properties: {
                  lat: { type: Type.NUMBER },
                  lng: { type: Type.NUMBER },
                },
                required: ['lat', 'lng'],
              },
            },
            stopsList: {
              type: Type.ARRAY,
              description: "An array of key stop details for BUS or METRO segments. Can be empty for other modes.",
              items: {
                type: Type.OBJECT,
                properties: {
                  name: { type: Type.STRING, description: "The name of the stop/station." },
                  platform: { type: Type.STRING, description: "Optional. The platform number, e.g., '3'." },
                  arrivalTime: { type: Type.STRING, description: "Optional. The estimated arrival time at this stop, e.g., '1:16 PM'." },
                  departureTime: { type: Type.STRING, description: "Optional. The estimated departure time from this stop, e.g., '1:17 PM'." },
                },
                required: ['name'],
              },
            },
          },
          required: ['mode', 'details', 'duration', 'path'],
        },
      },
    },
    required: ['id', 'routeName', 'totalDuration', 'totalCost', 'comfortScore', 'confidenceScore', 'summary', 'segments'],
  },
};

const getPreferenceDescription = (priority: Preference): string => {
  switch (priority) {
    case Preference.FASTEST:
      return "The user's absolute priority is minimizing travel time, even if it costs more or is less comfortable.";
    case Preference.CHEAPEST:
      return "The user wants the route with the lowest possible cost, and is willing to accept longer travel times or more transfers. For context, a cheap public transit fare in Delhi is typically under ₹30. Routes costing over ₹60 are considered expensive.";
    case Preference.COMFORT:
      return "The user prioritizes a comfortable journey. This means fewer transfers, less walking, and avoiding crowded lines if possible, even if it's slower or more expensive.";
    case Preference.BALANCED:
      return "The user is looking for a good balance between travel time, cost, and comfort. No single factor is an absolute priority.";
    default:
      return "Provide a balanced set of options.";
  }
};

const getSimulatedRealtimeDataForDelhi = (): string => {
  const conditions = [
    "Heavy traffic congestion reported on the Outer Ring Road near Nehru Place.",
    "Delhi Metro's Yellow Line is experiencing minor delays of 5-10 minutes due to a technical snag.",
    "Bus route 505 is currently diverted due to a public event near India Gate.",
    "High passenger traffic at Rajiv Chowk metro station; expect crowded platforms.",
    "Smooth traffic flow on the DND Flyway.",
    "Auto-rickshaw availability is low in the Connaught Place area.",
    "Delhi Transport Corporation (DTC) has reported that most buses are running on schedule.",
    "A traffic jam is reported on MG Road towards Gurugram."
  ];

  // Pick 2-3 random conditions to simulate a real-time scenario
  const shuffled = conditions.sort(() => 0.5 - Math.random());
  return shuffled.slice(0, Math.floor(Math.random() * 2) + 2).join('\n');
};


export const optimizeRouteWithAI = async (start: string, end: string, preferences: RoutePreferences): Promise<Route[]> => {
  const preferenceDescription = getPreferenceDescription(preferences.priority);
  const realtimeData = getSimulatedRealtimeDataForDelhi();

  const prompt = `
    You are an expert AI assistant for navigating Delhi's public transit system.
    Generate 3 distinct and optimized route options for the following request, taking into account the simulated real-time conditions.

    Start Location: ${start} (Approx. Lat/Lng: 28.6129, 77.2295)
    End Location: ${end} (Approx. Lat/Lng: 28.5517, 77.1983)
    User Preference: ${preferences.priority} (${preferenceDescription})

    Current Simulated Real-Time Conditions in Delhi:
    ---
    ${realtimeData}
    ---

    Instructions:
    1.  Generate three diverse routes. For example, if the user wants the cheapest route, one option should be the absolute cheapest (likely using buses), while others could be slightly more expensive but significantly faster (using the Metro).
    2.  Crucially, your suggestions MUST incorporate the real-time conditions provided. If a route is affected by a delay or congestion, mention it in the 'realtimeInfo' fields. If a route successfully avoids a problem, highlight that in the 'summary'.
    3.  For each BUS and METRO segment, you MUST provide a 'path' property containing a simplified array of 5-10 {lat, lng} coordinates representing its geographical path for map visualization. For WALK and AUTO_RICKSHAW segments, you can provide an empty array for the path.
    4.  Make the route details realistic for Delhi (e.g., use plausible metro lines like 'Yellow Line', 'Blue Line', or DTC bus routes like '505', '729').
    5.  Costs must be in Indian Rupees (INR). For the 'CHEAPEST' preference, prioritize routes that are significantly under ₹30.
    6.  Ensure segments connect logically. The coordinates of the end of one segment's path should be close to the start of the next.
    7.  Populate the 'realtimeInfo' fields at both the overall route level and the individual segment level where applicable to provide clear, actionable advice to the user.
    8.  For each BUS and METRO segment, populate the 'stopsList' property with a list of the most important stops (3-5 key stops are enough), including the start and end stops of the segment. Provide plausible arrival/departure times and platform numbers for each stop to create a realistic schedule view.
  `;

  try {
    const response = await ai.models.generateContent({
      model: "gemini-2.5-flash",
      contents: { parts: [{ text: prompt }] },
      config: {
        responseMimeType: "application/json",
        responseSchema: routeSchema,
      },
    });

    const jsonText = response.text.trim();
    const result = JSON.parse(jsonText) as Route[];
    
    // Sort results based on preference before returning
    return result.sort((a, b) => {
        switch (preferences.priority) {
            case Preference.FASTEST:
                return a.totalDuration - b.totalDuration;
            case Preference.CHEAPEST:
                return a.totalCost - b.totalCost;
            case Preference.COMFORT:
                return b.comfortScore - a.comfortScore;
            case Preference.BALANCED:
            default:
                return b.confidenceScore - a.confidenceScore;
        }
    });

  } catch (error) {
    console.error("Error calling Gemini API:", error);
    throw new Error("Failed to get route optimization from AI.");
  }
};