import express from 'express';
import { GoogleGenAI } from '@google/genai';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const port = parseInt(process.env.PORT || '3000', 10);

app.use(express.json());

const ai = new GoogleGenAI({
  apiKey: process.env.GEMINI_API_KEY,
  httpOptions: {
    headers: {
      'User-Agent': 'aistudio-build',
    },
  },
});

const SYSTEM_INSTRUCTION = `You are BhoomiMitra (भूमिमित्र / భూమిమిత్ర), the official intelligent AI Citizen Assistant for BhoomiSetu, India's National Land Acquisition & Management Portal.
You assist citizens, landowners, and stakeholders regarding land acquisition under:
- Right to Fair Compensation and Transparency in Land Acquisition, Rehabilitation and Resettlement Act, 2013 (RFCTLARR Act 2013)
- National Highways Act, 1956 (NH Act 1956)
- Statutory compensation valuation, 100% Solatium (Sec 30(1)), rural distance multiplier factors (1.25x - 2.0x), 12% additional market value (Sec 30(3))
- Direct Benefit Transfer (DBT) through Public Financial Management System (PFMS) into bank accounts
- Aadhaar eSign digital consent under Information Technology Act 2000
- Section 15(1) written objections, hearing notices, and CPGRAMS integrated grievances
- Land survey demarcations, DGPS cadastral rover pegging, and Village FMB maps

Tone: Highly respectful, authoritative yet warm and empathetic, clear, transparent, and reassuring.
Language: Answer in the same language the user asks in (English, Hindi, or Telugu). If Hindi, respond naturally in Devanagari script. If Telugu, respond in Telugu script. If English, respond in English.
Formatting: Use clean formatting with concise bullet points where appropriate.
Portal guidance: Guide users to relevant portal views when relevant (e.g. My Compensation, Land Demarcation, Digital Consent eSign, Documents Vault, or Grievance Portal).`;

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', service: 'BhoomiMitra AI' });
});

// POST /api/chat endpoint
app.post('/api/chat', async (req, res) => {
  try {
    const { message, language = 'en', context } = req.body;
    if (!message || typeof message !== 'string') {
      return res.status(400).json({ error: 'Message string is required' });
    }

    const citizenContextText = context
      ? `\n\n[Active Citizen Case Record]:
- Landowner: ${context.landownerName || 'Rajeshwar Rao'}
- Survey Number: ${context.surveyNumber || '145/2'}
- Land Extent: ${context.areaAcres || '2.5'} Acres (${context.landType || 'Agricultural'})
- Infrastructure Project: ${context.projectName || 'Hyderabad–Vijayawada Expressway (NH-65 Corridor Expansion)'}
- Location: Village ${context.village || 'Ghatkesar'}, Dist. ${context.district || 'Medchal-Malkajgiri'}, ${context.state || 'Telangana'}
- Total Sanctioned Award: ₹${Number(context.totalCompensation || 7225000).toLocaleString('en-IN')}
- Bank Account: State Bank of India (•••4892)
- Consent Status: ${context.consentStatus || 'Pending Digital Aadhaar eSign'}`
      : '';

    let reply = '';
    const modelsToTry = ['gemini-3.8-flash', 'gemini-3.1-flash-lite', 'gemini-flash-latest'];
    let lastError: any = null;

    for (const model of modelsToTry) {
      try {
        const response = await ai.models.generateContent({
          model,
          contents: [
            {
              role: 'user',
              parts: [
                {
                  text: `${SYSTEM_INSTRUCTION}${citizenContextText}\n\n[User preferred language: ${language}]\n[Citizen Query]: ${message}`,
                },
              ],
            },
          ],
        });
        if (response.text) {
          reply = response.text;
          break;
        }
      } catch (err: any) {
        lastError = err;
        console.warn(`Model ${model} unavailable, trying next:`, err?.message || err);
      }
    }

    if (!reply) {
      console.warn('AI models failed, using statutory knowledge fallback:', lastError?.message);
      const qLower = message.toLowerCase();
      if (qLower.includes('calculat') || qLower.includes('how much') || qLower.includes('formula') || qLower.includes('गणना') || qLower.includes('లెక్కిం')) {
        reply = language === 'hi'
          ? 'RFCTLARR अधिनियम 2013 की पहली अनुसूची के अनुसार, मुआवज़े की गणना इस प्रकार की जाती है:\n1. मूल बाज़ार दर × क्षेत्रफल\n2. ग्रामीण गुणक (1.5x)\n3. 100% अनिवार्य सोलेशियम (बाजार मूल्य का 100%)\n4. परिसंपत्ति मूल्यांकन (पेड़, कुएं, निर्माण)\n\nआपके सर्वे सं. 145/2 (2.5 एकड़) के लिए कुल स्वीकृत राशि ₹72,25,000 है जो सीधे आपके बैंक खाते में जमा होगी।'
          : language === 'te'
          ? 'RFCTLARR చట్టం 2013 ప్రకారం పరిహారం ఈ క్రింది విధంగా లెక్కించబడుతుంది:\n1. ప్రాథమిక మార్కెట్ విలువ × విస్తీర్ణం\n2. గ్రామీణ గుణకం (1.5x)\n3. 100% చట్టబద్ధమైన సొలేషియం\n4. ఆస్తుల విలువ (చెట్లు, బావులు)\n\nమీ సర్వే నం. 145/2 (2.5 ఎకరాలు) కోసం మొత్తం ₹72,25,000 మంజూరు చేయబడింది.'
          : 'Under the RFCTLARR Act 2013 (First Schedule), compensation is calculated using this statutory formula:\n\n1. Basic Market Rate × Area\n2. Rural Multiplier Factor (1.5x in your district)\n3. 100% Statutory Solatium (equal to 100% of market value)\n4. Asset Valuation (trees, wells, structures)\n5. 12% Per Annum Additional Market Value (from notification date)\n\nFor your Survey No. 145/2 (2.5 Acres), your sanctioned gross award is ₹72,25,000, deposited directly via PFMS DBT.';
      } else if (qLower.includes('when') || qLower.includes('bank') || qLower.includes('disburs') || qLower.includes('account') || qLower.includes('खाते') || qLower.includes('ఎప్పుడు') || qLower.includes('ఖాతా')) {
        reply = language === 'hi'
          ? 'मुआवजा राशि का भुगतान सार्वजनिक वित्तीय प्रबंधन प्रणाली (PFMS) के माध्यम से सीधे लाभार्थी के खाते (DBT) में किया जाता है:\n• आधार ई-हस्ताक्षर पूरा होने के बाद आदेश जारी होता है।\n• 3 से 7 कार्य दिवसों में राशि आपके भारतीय स्टेट बैंक (SBI •••4892) खाते में क्रेडिट हो जाएगी।'
          : language === 'te'
          ? 'పరిహారం చెల్లింపు PFMS DBT ద్వారా నేరుగా జరుగుతుంది:\n• మీరు ఆధార్ ఈ-సైన్ పూర్తి చేసిన వెంటనే ఆర్డర్ జారీ అవుతుంది.\n• 3 నుండి 7 పని దినాలలో మీ స్టేట్ బ్యాంక్ ఆఫ్ ఇండియా ఖాతాలో (•••4892) నగదు జమ అవుతుంది.'
          : 'Compensation disbursement takes place via Public Financial Management System (PFMS) Direct Benefit Transfer (DBT):\n\n• Once you execute digital Aadhaar eSign consent, the award is sealed by the Competent Authority (CALA).\n• Treasury bank mandate processes funds within 3 to 7 working days.\n• Funds are credited directly to your registered State Bank of India account (•••4892) without any middlemen.';
      } else {
        reply = language === 'hi'
          ? `आपके प्रश्न के संबंध में:\n\nभूमि अधिग्रहण एवं पुनर्वास अधिनियम 2013 के अनुसार, आपके समस्त विधिक अधिकार पूर्णतः सुरक्षित हैं। सर्वे सं. 145/2 (2.5 एकड़) के लिए 100% सोलेशियम सहित कुल ₹72,25,000 की राशि स्वीकृत है। आप पोर्टल के माध्यम से सीधे मुआवज़ा आदेश देख सकते हैं या शिकायत दर्ज कर सकते हैं।`
          : language === 'te'
          ? `మీ ప్రశ్న గురించి:\n\nRFCTLARR చట్టం 2013 ప్రకారం మీ సర్వే నెం. 145/2 (2.5 ఎకరాలు) కు 100% సొలేషియంతో కలిపి ₹72,25,000 పరిహారం నిర్ణయించబడింది. మీరు పోర్టల్ ద్వారా పరిహార వివరాలు చూడవచ్చు లేదా నేరుగా ఆన్‌లైన్‌లో వినతిపత్రం దాఖలు చేయవచ్చు.`
          : `Regarding your land inquiry:\n\nUnder statutory provisions of RFCTLARR Act 2013 & NH Act 1956, your survey particulars (Sy 145/2, 2.5 Acres) have completed Section 3D declaration. You are entitled to 100% Solatium plus statutory interest totaling ₹72,25,000. You can inspect your itemized valuation or file a formal inquiry directly on BhoomiSetu.`;
      }
    }

    return res.json({ reply });
  } catch (error: any) {
    console.error('BhoomiMitra API error:', error?.message || error);
    return res.status(200).json({
      reply: 'Namaste! BhoomiMitra is currently reviewing statutory land records for your survey parcel. Your compensation rights under RFCTLARR Act 2013 are completely safeguarded with 100% Solatium. Please feel free to inspect your compensation award or grievance status in the Citizen Portal.',
    });
  }
});

// Vite middleware in dev or static serving in prod
const isProduction = process.env.NODE_ENV === 'production';

if (!isProduction) {
  const { createServer: createViteServer } = await import('vite');
  const vite = await createViteServer({
    server: { middlewareMode: true, host: '0.0.0.0', port },
    appType: 'spa',
  });
  app.use(vite.middlewares);
} else {
  app.use(express.static(path.resolve(__dirname, 'dist')));
  app.get('*', (req, res) => {
    res.sendFile(path.resolve(__dirname, 'dist', 'index.html'));
  });
}

app.listen(port, '0.0.0.0', () => {
  console.log(`BhoomiSetu Server listening on port ${port} (mode: ${isProduction ? 'prod' : 'dev'})`);
});
