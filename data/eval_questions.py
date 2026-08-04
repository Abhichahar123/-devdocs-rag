# Har question ek dictionary hai: question, ground_truth answer, aur category
# Categories: "easy" (direct wording), "medium" (paraphrased), "hard" (trick/unrelated)

EVAL_QUESTIONS = [
    # ===== EASY (direct, docs-jaisi wording) =====
    {
        "question": "How do I capture an authorized payment?",
        "ground_truth": "You can capture an authorized payment either manually from the Dashboard (Transactions → Payments → Capture Payment) or automatically by enabling Auto-capture with a timeout period in payment capture settings.",
        "category": "easy",
    },
    {
        "question": "What is Razorpay's settlement schedule?",
        "ground_truth": "Razorpay settles payments received from customers to your bank account as per a settlement schedule, which can be checked and configured from the Dashboard.",
        "category": "easy",
    },
    {
        "question": "How do I view detailed settlement breakdown?",
        "ground_truth": "You can use the settlement_id to view the detailed breakdown of a settlement from the Dashboard.",
        "category": "easy",
    },
    {
        "question": "What are test card details used for?",
        "ground_truth": "Test card details are used to simulate the payment flow with available payment methods, using any CVV and any future expiry date, without making a real transaction.",
        "category": "easy",
    },
    {
        "question": "How do I accept a dispute raised by a customer?",
        "ground_truth": "You can accept a dispute, in which case the customer is refunded. In cases of fraud, you must refund the amount.",
        "category": "easy",
    },
    {
        "question": "What is the Payments API used for?",
        "ground_truth": "The Payments APIs let you perform various actions such as Capture, Fetch, and Update on payments, some of which can also be done from the Dashboard.",
        "category": "easy",
    },
    {
        "question": "How are webhooks delivered?",
        "ground_truth": "Webhooks are the primary and most efficient method for event notifications, and they are delivered asynchronously in near real-time.",
        "category": "easy",
    },
    {
        "question": "What is Razorpay Route used for?",
        "ground_truth": "Razorpay Route is used to split payments and automatically transfer funds to multiple linked accounts (such as vendors or partners).",
        "category": "easy",
    },
    {
        "question": "How do I set up Automatic Capture with a Timeout option?",
        "ground_truth": "You can configure Automatic Capture with a Timeout to auto-capture authorized payments within a specific time period, such as within 2 days from creation.",
        "category": "easy",
    },
    {
        "question": "Are payment links supported by Razorpay?",
        "ground_truth": "Yes, Razorpay provides Payment Links APIs to create and manage payment links for accepting payments.",
        "category": "easy",
    },

    # ===== MEDIUM (paraphrased, indirect wording) =====
    {
        "question": "What happens if I don't collect the money from a customer in time?",
        "ground_truth": "Payments that are not captured within the specified timeout period are automatically refunded to the customer.",
        "category": "medium",
    },
    {
        "question": "Can customers dispute a transaction if they're unhappy?",
        "ground_truth": "Yes, customers can raise disputes; the merchant can either accept the dispute (resulting in a refund) or contest it.",
        "category": "medium",
    },
    {
        "question": "How do I know when money actually reaches my bank account?",
        "ground_truth": "Money reaches your bank account through settlements, which follow a defined settlement schedule that you can monitor from the Dashboard.",
        "category": "medium",
    },
    {
        "question": "Is there a way to split a payment between multiple people automatically?",
        "ground_truth": "Yes, this can be done using Razorpay Route, which automatically transfers portions of a payment to multiple linked accounts.",
        "category": "medium",
    },
    {
        "question": "How do I get notified in real time when a payment event happens?",
        "ground_truth": "You can use Webhooks, which deliver event notifications asynchronously in near real-time.",
        "category": "medium",
    },
    {
        "question": "Can I test my integration without using real money?",
        "ground_truth": "Yes, you can use test card details with any CVV and future expiry date to simulate payments without real transactions.",
        "category": "medium",
    },
    {
        "question": "What's the difference between manual and automatic payment capture?",
        "ground_truth": "Manual capture requires you to capture the payment yourself from the Dashboard, while automatic capture uses configured settings to capture payments automatically, optionally within a timeout period.",
        "category": "medium",
    },
    {
        "question": "Do I need to do anything for customer payments to reach me?",
        "ground_truth": "No action is required from your end for payments to be settled; Razorpay automatically settles payments as per the settlement schedule.",
        "category": "medium",
    },
    {
        "question": "What should I do if a customer claims fraud on their payment?",
        "ground_truth": "In cases of fraud, you must refund the transaction amount when the dispute is raised.",
        "category": "medium",
    },
    {
        "question": "Can I share a simple link with customers to collect payments?",
        "ground_truth": "Yes, Payment Links allow you to create shareable links for customers to make payments without needing a full checkout integration.",
        "category": "medium",
    },

    # ===== HARD (unrelated / trick / not covered in docs) =====
    {
        "question": "What is Razorpay's stock price?",
        "ground_truth": "I don't have information on this in the provided documentation.",
        "category": "hard",
    },
    {
        "question": "What is the capital of India?",
        "ground_truth": "I don't have information on this in the provided documentation.",
        "category": "hard",
    },
    {
        "question": "Who is the CEO of Razorpay?",
        "ground_truth": "I don't have information on this in the provided documentation.",
        "category": "hard",
    },
    {
        "question": "Does Razorpay support cryptocurrency payments?",
        "ground_truth": "I don't have information on this in the provided documentation.",
        "category": "hard",
    },
    {
        "question": "What is the weather like today?",
        "ground_truth": "I don't have information on this in the provided documentation.",
        "category": "hard",
    },
]