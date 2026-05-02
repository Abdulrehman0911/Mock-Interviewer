export interface Company {
  id: string;
  name: string;
  description: string;
  initials: string;
  color: string;
}

// All 12 roles that exist in the backend JSON
export const ALL_ROLES = [
  "Software Engineer",
  "Data Scientist",
  "Product Manager",
  "DevOps Engineer",
  "Frontend Developer",
  "Backend Developer",
  "Mobile Developer",
  "Cloud Engineer",
  "Machine Learning Engineer",
  "Systems Engineer",
  "Quality Assurance Engineer",
  "AI Engineer",
];

export const COMPANIES: Company[] = [
  { id: "google",       name: "Google",               description: "Search, Cloud & AI engineering",           initials: "G",    color: "#4285F4" },
  { id: "microsoft",    name: "Microsoft",             description: "Azure, Office & Enterprise solutions",     initials: "MS",   color: "#00A4EF" },
  { id: "amazon",       name: "Amazon",                description: "AWS, E-commerce & Logistics",             initials: "AMZ",  color: "#FF9900" },
  { id: "meta",         name: "Meta",                  description: "Social media, VR/AR & AI infrastructure", initials: "META", color: "#1877F2" },
  { id: "apple",        name: "Apple",                 description: "iOS, macOS & Hardware engineering",       initials: "AAPL", color: "#A2AAAD" },
  { id: "netflix",      name: "Netflix",               description: "Streaming, content & platform tech",      initials: "NFLX", color: "#E50914" },
  { id: "systems-ltd",  name: "Systems Ltd",           description: "Pakistan's leading software house",       initials: "SYS",  color: "#2E7D32" },
  { id: "netsol",       name: "NetSol Technologies",   description: "Global IT company based in Pakistan",     initials: "NTL",  color: "#1565C0" },
];

export function getCompanyById(id: string): Company | undefined {
  return COMPANIES.find((c) => c.id === id);
}
