// Bundled offline first-aid pack — lets AarogyaBot still give safe, critical
// guidance when there is no network (key for 2G / no-signal rural areas).

const EMERGENCY = {
  keywords: ['snake', 'bite', 'bleeding', 'unconscious', 'not breathing', 'chest pain', 'drowning', 'burn', 'poison', 'fits', 'seizure'],
  triage: {
    level: 'EMERGENCY',
    action: 'This may be an emergency. Call 108 for an ambulance and reach the nearest hospital immediately.',
    color: 'red',
  },
}

const RULES = [
  {
    match: ['snake'],
    text: 'Snake bite: Keep the person calm and still. Keep the bitten limb below heart level and do NOT move it. Remove rings/bangles. Do NOT cut, suck, or tie tightly. Reach a hospital for anti-snake venom immediately.',
  },
  {
    match: ['bleeding', 'cut', 'wound'],
    text: 'Heavy bleeding: Press firmly on the wound with a clean cloth and do not lift to check. Raise the part above the heart if possible. Add more cloth on top if it soaks through. Go to a hospital if it does not stop.',
  },
  {
    match: ['burn'],
    text: 'Burns: Cool under clean running water for 15–20 minutes. Do NOT apply toothpaste, oil, or ice. Cover loosely with a clean cloth. Seek care for large or deep burns.',
  },
  {
    match: ['diarrhea', 'diarrhoea', 'loose', 'vomit'],
    text: 'Diarrhoea/vomiting: Prevent dehydration — sip ORS after each loose stool (mix 6 tsp sugar + ½ tsp salt in 1 litre clean water if no packet). Keep eating. See a doctor if there is blood, high fever, or no urine for 8 hours.',
  },
  {
    match: ['fever'],
    text: 'Fever: Rest, drink plenty of clean fluids, and sponge with room-temperature water. Paracetamol can help. See a doctor if fever is above 103°F, lasts over 3 days, or comes with a stiff neck or difficulty breathing.',
  },
  {
    match: ['dehydrat', 'thirst'],
    text: 'Dehydration: Sit in shade and sip ORS, clean water, or coconut water. Seek care for no urination over 8 hours, confusion, or sunken eyes.',
  },
  {
    match: ['choking'],
    text: 'Choking: If the person cannot breathe or speak, give 5 firm back blows between the shoulder blades, then abdominal thrusts, until the object comes out. Call for help if they collapse.',
  },
]

const DEFAULT_TEXT =
  'You are offline, so I am giving basic first-aid guidance only. For any serious or worsening symptom, visit your nearest PHC. In an emergency, call 108.'

export function getOfflineReply(message) {
  const text = (message || '').toLowerCase()

  const isEmergency = EMERGENCY.keywords.some((k) => text.includes(k))

  const matched = RULES.find((r) => r.match.some((k) => text.includes(k)))
  const reply = matched ? matched.text : DEFAULT_TEXT

  return {
    reply: `(Offline) ${reply}`,
    triage: isEmergency ? EMERGENCY.triage : null,
  }
}
