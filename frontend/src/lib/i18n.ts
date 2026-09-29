export type Language = "en" | "hi" | "ne";

export const languageNames: Record<Language, string> = {
  en: "English",
  hi: "हिन्दी",
  ne: "नेपाली",
};

const copy = {
  en: {
    workspace: "Workspace",
    monitoredSprings: "Monitored springs",
    priorityZones: "Priority recharge zones",
    meanSuitability: "Mean suitability",
    modelConfidence: "Model confidence",
    demoRecords: "DEMO RECORDS",
    storedRecords: "Stored records",
    listedActive: "listed as active",
    noBoundaries: "No mapped boundaries supplied",
    noValidatedAnalysis: "No validated analysis",
    sourcedGis: "Requires sourced GIS inputs",
    confidenceAccuracy: "Confidence is not accuracy",
    noValidatedModel: "No validated model",
    seeProvenance: "See model provenance",
    latestData: "Latest available data",
    unverifiedData: "Unverified data",
    apiUnavailable: "DEMO DATA · API unavailable",
    apiConnected: "DEMO DATA · API connected",
  },
  hi: {
    workspace: "कार्यस्थल",
    monitoredSprings: "निगरानी किए गए स्रोत",
    priorityZones: "प्राथमिक रिचार्ज क्षेत्र",
    meanSuitability: "औसत उपयुक्तता",
    modelConfidence: "मॉडल विश्वास",
    demoRecords: "डेमो रिकॉर्ड",
    storedRecords: "संग्रहीत रिकॉर्ड",
    listedActive: "सक्रिय सूचीबद्ध",
    noBoundaries: "मानचित्र सीमाएं उपलब्ध नहीं",
    noValidatedAnalysis: "सत्यापित विश्लेषण नहीं",
    sourcedGis: "स्रोत GIS इनपुट आवश्यक",
    confidenceAccuracy: "विश्वास सटीकता नहीं है",
    noValidatedModel: "सत्यापित मॉडल नहीं",
    seeProvenance: "मॉडल स्रोत देखें",
    latestData: "नवीनतम उपलब्ध डेटा",
    unverifiedData: "असत्यापित डेटा",
    apiUnavailable: "डेमो डेटा · API उपलब्ध नहीं",
    apiConnected: "डेमो डेटा · API जुड़ा है",
  },
  ne: {
    workspace: "कार्यस्थान",
    monitoredSprings: "अनुगमन गरिएका मुहान",
    priorityZones: "प्राथमिक रिचार्ज क्षेत्र",
    meanSuitability: "औसत उपयुक्तता",
    modelConfidence: "मोडेल विश्वास",
    demoRecords: "डेमो रेकर्ड",
    storedRecords: "भण्डारित रेकर्ड",
    listedActive: "सक्रिय सूची",
    noBoundaries: "नक्सा सीमा उपलब्ध छैन",
    noValidatedAnalysis: "प्रमाणित विश्लेषण छैन",
    sourcedGis: "स्रोत GIS इनपुट आवश्यक",
    confidenceAccuracy: "विश्वास शुद्धता होइन",
    noValidatedModel: "प्रमाणित मोडेल छैन",
    seeProvenance: "मोडेल स्रोत हेर्नुहोस्",
    latestData: "नवीनतम उपलब्ध डाटा",
    unverifiedData: "अपुष्ट डाटा",
    apiUnavailable: "डेमो डाटा · API उपलब्ध छैन",
    apiConnected: "डेमो डाटा · API जोडिएको छ",
  },
} as const;

export function getCopy(language: Language) {
  return copy[language];
}
