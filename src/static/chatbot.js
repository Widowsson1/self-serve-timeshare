// SelfServe Timeshare Intelligent Chatbot
class TimeshareChatbot {
    constructor() {
        this.isOpen = false;
        this.currentFlow = 'welcome';
        this.userContext = {
            name: null,
            email: null,
            hasTimeshare: null,
            interestedIn: null,
            priceRange: null,
            timeline: null
        };
        this.init();
    }

    init() {
        this.createChatWidget();
        this.bindEvents();
        
        // Auto-open after 10 seconds if user hasn't interacted
        setTimeout(() => {
            if (!this.isOpen && !localStorage.getItem('chatbot_dismissed')) {
                this.openChat();
                this.addMessage('bot', "👋 Hi! I'm here to help you sell or rent your timeshare commission-free. Have any questions?");
            }
        }, 10000);
    }

    createChatWidget() {
        const chatHTML = `
            <div id="chatbot-container" class="chatbot-container">
                <div id="chatbot-button" class="chatbot-button">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    <span class="chatbot-notification" id="chatbot-notification">1</span>
                </div>
                
                <div id="chatbot-widget" class="chatbot-widget">
                    <div class="chatbot-header">
                        <div class="chatbot-header-info">
                            <div class="chatbot-avatar">🤖</div>
                            <div>
                                <div class="chatbot-title">SelfServe Assistant</div>
                                <div class="chatbot-status">Online • Typically replies instantly</div>
                            </div>
                        </div>
                        <button id="chatbot-close" class="chatbot-close">×</button>
                    </div>
                    
                    <div id="chatbot-messages" class="chatbot-messages">
                        <div class="chatbot-message bot-message">
                            <div class="message-content">
                                <p>👋 Welcome to SelfServe Timeshare! I'm here to help you sell or rent your timeshare commission-free.</p>
                                <p>What brings you here today?</p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="chatbot-quick-replies" id="chatbot-quick-replies">
                        <button class="quick-reply" onclick="chatbot.handleQuickReply('sell')">💰 I want to sell</button>
                        <button class="quick-reply" onclick="chatbot.handleQuickReply('rent')">🏖️ I want to rent</button>
                        <button class="quick-reply" onclick="chatbot.handleQuickReply('learn')">📚 Learn more</button>
                        <button class="quick-reply" onclick="chatbot.handleQuickReply('pricing')">💳 See pricing</button>
                    </div>
                    
                    <div class="chatbot-input-area">
                        <input type="text" id="chatbot-input" placeholder="Type your message..." maxlength="500">
                        <button id="chatbot-send">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="m22 2-7 20-4-9-9-4z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', chatHTML);
        this.addChatStyles();
    }

    addChatStyles() {
        const styles = `
            <style>
                .chatbot-container {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    z-index: 10000;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                }

                .chatbot-button {
                    width: 60px;
                    height: 60px;
                    background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    cursor: pointer;
                    box-shadow: 0 4px 20px rgba(37, 99, 235, 0.3);
                    transition: all 0.3s ease;
                    color: white;
                    position: relative;
                }

                .chatbot-button:hover {
                    transform: scale(1.1);
                    box-shadow: 0 6px 25px rgba(37, 99, 235, 0.4);
                }

                .chatbot-notification {
                    position: absolute;
                    top: -5px;
                    right: -5px;
                    background: #ef4444;
                    color: white;
                    border-radius: 50%;
                    width: 20px;
                    height: 20px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 12px;
                    font-weight: bold;
                }

                .chatbot-widget {
                    position: absolute;
                    bottom: 80px;
                    right: 0;
                    width: 380px;
                    height: 500px;
                    background: white;
                    border-radius: 16px;
                    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
                    display: none;
                    flex-direction: column;
                    overflow: hidden;
                }

                .chatbot-widget.open {
                    display: flex;
                    animation: slideUp 0.3s ease-out;
                }

                @keyframes slideUp {
                    from {
                        opacity: 0;
                        transform: translateY(20px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }

                .chatbot-header {
                    background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
                    color: white;
                    padding: 16px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }

                .chatbot-header-info {
                    display: flex;
                    align-items: center;
                    gap: 12px;
                }

                .chatbot-avatar {
                    width: 40px;
                    height: 40px;
                    background: rgba(255, 255, 255, 0.2);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 18px;
                }

                .chatbot-title {
                    font-weight: 600;
                    font-size: 16px;
                }

                .chatbot-status {
                    font-size: 12px;
                    opacity: 0.8;
                }

                .chatbot-close {
                    background: none;
                    border: none;
                    color: white;
                    font-size: 24px;
                    cursor: pointer;
                    padding: 0;
                    width: 30px;
                    height: 30px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border-radius: 50%;
                    transition: background-color 0.2s;
                }

                .chatbot-close:hover {
                    background: rgba(255, 255, 255, 0.2);
                }

                .chatbot-messages {
                    flex: 1;
                    padding: 16px;
                    overflow-y: auto;
                    display: flex;
                    flex-direction: column;
                    gap: 12px;
                }

                .chatbot-message {
                    display: flex;
                    align-items: flex-start;
                    gap: 8px;
                }

                .bot-message {
                    justify-content: flex-start;
                }

                .user-message {
                    justify-content: flex-end;
                }

                .message-content {
                    max-width: 80%;
                    padding: 12px 16px;
                    border-radius: 18px;
                    line-height: 1.4;
                }

                .bot-message .message-content {
                    background: #f1f5f9;
                    color: #374151;
                }

                .user-message .message-content {
                    background: #2563eb;
                    color: white;
                }

                .message-content p {
                    margin: 0 0 8px 0;
                }

                .message-content p:last-child {
                    margin-bottom: 0;
                }

                .chatbot-quick-replies {
                    padding: 0 16px 16px;
                    display: flex;
                    flex-wrap: wrap;
                    gap: 8px;
                }

                .quick-reply {
                    background: #f1f5f9;
                    border: 1px solid #e2e8f0;
                    border-radius: 20px;
                    padding: 8px 16px;
                    font-size: 14px;
                    cursor: pointer;
                    transition: all 0.2s;
                    color: #374151;
                }

                .quick-reply:hover {
                    background: #e2e8f0;
                    border-color: #cbd5e1;
                }

                .chatbot-input-area {
                    padding: 16px;
                    border-top: 1px solid #e2e8f0;
                    display: flex;
                    gap: 8px;
                }

                .chatbot-input-area input {
                    flex: 1;
                    border: 1px solid #e2e8f0;
                    border-radius: 20px;
                    padding: 10px 16px;
                    outline: none;
                    font-size: 14px;
                }

                .chatbot-input-area input:focus {
                    border-color: #2563eb;
                }

                .chatbot-input-area button {
                    width: 40px;
                    height: 40px;
                    background: #2563eb;
                    border: none;
                    border-radius: 50%;
                    color: white;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: background-color 0.2s;
                }

                .chatbot-input-area button:hover {
                    background: #1d4ed8;
                }

                .typing-indicator {
                    display: flex;
                    align-items: center;
                    gap: 4px;
                    padding: 12px 16px;
                    background: #f1f5f9;
                    border-radius: 18px;
                    max-width: 80px;
                }

                .typing-dot {
                    width: 6px;
                    height: 6px;
                    background: #9ca3af;
                    border-radius: 50%;
                    animation: typing 1.4s infinite;
                }

                .typing-dot:nth-child(2) {
                    animation-delay: 0.2s;
                }

                .typing-dot:nth-child(3) {
                    animation-delay: 0.4s;
                }

                @keyframes typing {
                    0%, 60%, 100% {
                        transform: translateY(0);
                    }
                    30% {
                        transform: translateY(-10px);
                    }
                }

                @media (max-width: 480px) {
                    .chatbot-widget {
                        width: calc(100vw - 40px);
                        height: 70vh;
                        bottom: 80px;
                        right: 20px;
                        left: 20px;
                    }
                }
            </style>
        `;
        document.head.insertAdjacentHTML('beforeend', styles);
    }

    bindEvents() {
        document.getElementById('chatbot-button').addEventListener('click', () => {
            this.toggleChat();
        });

        document.getElementById('chatbot-close').addEventListener('click', () => {
            this.closeChat();
        });

        document.getElementById('chatbot-send').addEventListener('click', () => {
            this.sendMessage();
        });

        document.getElementById('chatbot-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
    }

    toggleChat() {
        if (this.isOpen) {
            this.closeChat();
        } else {
            this.openChat();
        }
    }

    openChat() {
        this.isOpen = true;
        document.getElementById('chatbot-widget').classList.add('open');
        document.getElementById('chatbot-notification').style.display = 'none';
        localStorage.setItem('chatbot_dismissed', 'true');
    }

    closeChat() {
        this.isOpen = false;
        document.getElementById('chatbot-widget').classList.remove('open');
    }

    sendMessage() {
        const input = document.getElementById('chatbot-input');
        const message = input.value.trim();
        
        if (message) {
            this.addMessage('user', message);
            input.value = '';
            this.processUserMessage(message);
        }
    }

    addMessage(sender, content, showTyping = false) {
        const messagesContainer = document.getElementById('chatbot-messages');
        
        if (showTyping && sender === 'bot') {
            this.showTypingIndicator();
            setTimeout(() => {
                this.hideTypingIndicator();
                this.addActualMessage(sender, content);
            }, 1500);
        } else {
            this.addActualMessage(sender, content);
        }
    }

    addActualMessage(sender, content) {
        const messagesContainer = document.getElementById('chatbot-messages');
        const messageClass = sender === 'bot' ? 'bot-message' : 'user-message';
        
        const messageHTML = `
            <div class="chatbot-message ${messageClass}">
                <div class="message-content">
                    ${typeof content === 'string' ? `<p>${content}</p>` : content}
                </div>
            </div>
        `;
        
        messagesContainer.insertAdjacentHTML('beforeend', messageHTML);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    showTypingIndicator() {
        const messagesContainer = document.getElementById('chatbot-messages');
        const typingHTML = `
            <div class="chatbot-message bot-message typing-message">
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        `;
        messagesContainer.insertAdjacentHTML('beforeend', typingHTML);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    hideTypingIndicator() {
        const typingMessage = document.querySelector('.typing-message');
        if (typingMessage) {
            typingMessage.remove();
        }
    }

    handleQuickReply(action) {
        this.hideQuickReplies();
        
        switch (action) {
            case 'sell':
                this.addMessage('user', '💰 I want to sell');
                this.handleSellFlow();
                break;
            case 'rent':
                this.addMessage('user', '🏖️ I want to rent');
                this.handleRentFlow();
                break;
            case 'learn':
                this.addMessage('user', '📚 Learn more');
                this.handleLearnFlow();
                break;
            case 'pricing':
                this.addMessage('user', '💳 See pricing');
                this.handlePricingFlow();
                break;
        }
    }

    hideQuickReplies() {
        document.getElementById('chatbot-quick-replies').style.display = 'none';
    }

    showQuickReplies(replies) {
        const container = document.getElementById('chatbot-quick-replies');
        container.innerHTML = '';
        
        replies.forEach(reply => {
            const button = document.createElement('button');
            button.className = 'quick-reply';
            button.textContent = reply.text;
            button.onclick = () => reply.action();
            container.appendChild(button);
        });
        
        container.style.display = 'flex';
    }

    handleSellFlow() {
        setTimeout(() => {
            this.addMessage('bot', `Great choice! 🎉 Selling your timeshare commission-free can save you thousands compared to traditional brokers.

Here's what makes us different:
• Keep 100% of your sale proceeds
• No commission fees (brokers charge 15-40%)
• Direct buyer contact
• Professional listing tools
• Market insights and pricing guidance

What type of timeshare are you looking to sell?`, true);
            
            this.showQuickReplies([
                { text: '🏖️ Beach Resort', action: () => this.handleTimeshareType('beach') },
                { text: '🏔️ Mountain/Ski', action: () => this.handleTimeshareType('mountain') },
                { text: '🏙️ City/Urban', action: () => this.handleTimeshareType('city') },
                { text: '🌴 Tropical/Island', action: () => this.handleTimeshareType('tropical') }
            ]);
        }, 1000);
    }

    handleRentFlow() {
        setTimeout(() => {
            this.addMessage('bot', `Perfect! 🏖️ Renting your timeshare is a great way to generate income while you decide whether to sell.

Benefits of our rental platform:
• Keep 100% of rental income
• No commission or booking fees
• Direct renter communication
• Flexible rental terms
• Multiple year availability

Are you looking to rent out specific weeks or the entire year?`, true);
            
            this.showQuickReplies([
                { text: '📅 Specific weeks', action: () => this.handleRentalType('weeks') },
                { text: '📆 Entire year', action: () => this.handleRentalType('year') },
                { text: '🤔 Not sure yet', action: () => this.handleRentalType('unsure') }
            ]);
        }, 1000);
    }

    handleLearnFlow() {
        setTimeout(() => {
            this.addMessage('bot', `I'd love to explain how SelfServe Timeshare works! 📚

**The Problem with Traditional Brokers:**
• Charge 15-40% commission (thousands of dollars!)
• Limited control over your listing
• Slow communication with buyers
• Hidden fees and costs

**Our Solution:**
• Simple monthly subscription ($7.99-$39.99)
• Keep 100% of proceeds
• Direct buyer/renter contact
• Professional tools and support
• Cancel anytime

What would you like to know more about?`, true);
            
            this.showQuickReplies([
                { text: '💰 Cost comparison', action: () => this.handleCostComparison() },
                { text: '🛠️ Platform features', action: () => this.handleFeatures() },
                { text: '📈 Success stories', action: () => this.handleSuccessStories() },
                { text: '🚀 Getting started', action: () => this.handleGettingStarted() }
            ]);
        }, 1000);
    }

    handlePricingFlow() {
        setTimeout(() => {
            this.addMessage('bot', `Here are our simple, transparent pricing plans: 💳

**Starter - $7.99/month**
• 1 property listing
• Sale OR rental
• 6 photos
• Basic analytics
• Email support

**Basic - $14.99/month** ⭐ Most Popular
• 2 property listings  
• Sale AND rental
• 10 photos
• Advanced analytics
• Priority support

**Premium - $24.99/month**
• 5 property listings
• Featured placement
• 20 photos
• Premium analytics

**Unlimited - $39.99/month**
• Unlimited listings
• Top placement
• 30 photos
• API access

All plans include our money-back guarantee! Which plan interests you most?`, true);
            
            this.showQuickReplies([
                { text: '🚀 Start with Basic', action: () => this.handleSignup('basic') },
                { text: '💎 Try Premium', action: () => this.handleSignup('premium') },
                { text: '💰 Compare savings', action: () => this.handleSavingsCalculator() },
                { text: '❓ Which plan for me?', action: () => this.handlePlanRecommendation() }
            ]);
        }, 1000);
    }

    handleTimeshareType(type) {
        this.userContext.timeshareType = type;
        this.hideQuickReplies();
        
        const typeNames = {
            beach: 'Beach Resort',
            mountain: 'Mountain/Ski Resort', 
            city: 'City/Urban Property',
            tropical: 'Tropical/Island Resort'
        };
        
        this.addMessage('user', `🏖️ ${typeNames[type]}`);
        
        setTimeout(() => {
            this.addMessage('bot', `Excellent! ${typeNames[type]} timeshares are in high demand. 

To help you get the best results, what's your main goal?`, true);
            
            this.showQuickReplies([
                { text: '💸 Sell quickly', action: () => this.handleGoal('quick') },
                { text: '💰 Get best price', action: () => this.handleGoal('price') },
                { text: '📊 See market value', action: () => this.handleGoal('value') },
                { text: '🚀 Get started now', action: () => this.handleSignup('sell') }
            ]);
        }, 1000);
    }

    handleGoal(goal) {
        this.userContext.goal = goal;
        this.hideQuickReplies();
        
        const goalTexts = {
            quick: '💸 Sell quickly',
            price: '💰 Get best price', 
            value: '📊 See market value'
        };
        
        this.addMessage('user', goalTexts[goal]);
        
        setTimeout(() => {
            let response = '';
            
            switch (goal) {
                case 'quick':
                    response = `Smart strategy! For quick sales, I recommend:

• **Competitive pricing** (5-10% below market)
• **High-quality photos** (all angles + amenities)
• **Detailed descriptions** highlighting unique features
• **Quick response** to inquiries (within 2 hours)

Our Basic plan ($14.99/month) gives you everything needed for a fast sale. Ready to get started?`;
                    break;
                case 'price':
                    response = `Great approach! To maximize your sale price:

• **Market research** using our comparable sales data
• **Professional photos** showcasing your unit's best features  
• **Strategic timing** (peak booking seasons)
• **Highlight unique amenities** and location benefits

Our Premium plan ($24.99/month) includes featured placement and advanced analytics to help you get top dollar. Interested?`;
                    break;
                case 'value':
                    response = `Perfect! Understanding your timeshare's value is crucial.

Our platform provides:
• **Comparable sales data** for your resort
• **Market trend analysis** 
• **Pricing recommendations** based on unit type, season, location
• **Performance tracking** to optimize your listing

Would you like me to help you get a free market analysis for your timeshare?`;
                    break;
            }
            
            this.addMessage('bot', response, true);
            
            this.showQuickReplies([
                { text: '🚀 Yes, get started!', action: () => this.handleSignup('sell') },
                { text: '📊 Free market analysis', action: () => this.handleMarketAnalysis() },
                { text: '💬 Talk to expert', action: () => this.handleExpertContact() }
            ]);
        }, 1000);
    }

    handleSavingsCalculator() {
        this.hideQuickReplies();
        this.addMessage('user', '💰 Compare savings');
        
        setTimeout(() => {
            this.addMessage('bot', `Let me show you the savings! 💰

**Traditional Broker Example:**
• Timeshare sells for $15,000
• Broker commission (25%): -$3,750
• Your net proceeds: $11,250

**SelfServe Timeshare:**
• Timeshare sells for $15,000  
• Monthly fee (3 months): -$45
• Your net proceeds: $14,955

**You save: $3,705!** 🎉

Even if it takes 6 months to sell, you still save over $3,600 compared to broker fees.

Ready to keep more of your money?`, true);
            
            this.showQuickReplies([
                { text: '🚀 Start saving now', action: () => this.handleSignup('basic') },
                { text: '📱 Calculate my savings', action: () => this.handlePersonalCalculator() },
                { text: '❓ More questions', action: () => this.handleMoreQuestions() }
            ]);
        }, 1000);
    }

    handleSignup(plan) {
        this.hideQuickReplies();
        
        setTimeout(() => {
            this.addMessage('bot', `Fantastic! 🎉 I'm excited to help you get started.

To create your account and begin listing your timeshare:

1. **Click "Get Started"** on our homepage
2. **Choose your plan** (you can always upgrade later)
3. **Add your timeshare details** (takes 5-10 minutes)
4. **Upload photos** (we'll help you get great shots)
5. **Go live** and start connecting with buyers!

You'll also get:
• Welcome email with tips for success
• Access to our seller resources
• Direct support from our team

Ready to take the next step?`, true);
            
            this.showQuickReplies([
                { text: '🚀 Create account now', action: () => this.redirectToSignup() },
                { text: '📞 Call me instead', action: () => this.handlePhoneContact() },
                { text: '📧 Email me details', action: () => this.handleEmailContact() }
            ]);
        }, 1000);
    }

    redirectToSignup() {
        this.addMessage('user', '🚀 Create account now');
        this.addMessage('bot', 'Perfect! Redirecting you to get started... 🚀');
        
        setTimeout(() => {
            window.open('/#pricing', '_blank');
        }, 1500);
    }

    processUserMessage(message) {
        const lowerMessage = message.toLowerCase();
        
        // Simple keyword matching for common questions
        if (lowerMessage.includes('price') || lowerMessage.includes('cost') || lowerMessage.includes('fee')) {
            this.handlePricingFlow();
        } else if (lowerMessage.includes('sell')) {
            this.handleSellFlow();
        } else if (lowerMessage.includes('rent')) {
            this.handleRentFlow();
        } else if (lowerMessage.includes('how') || lowerMessage.includes('work')) {
            this.handleLearnFlow();
        } else if (lowerMessage.includes('contact') || lowerMessage.includes('phone') || lowerMessage.includes('call')) {
            this.handleContactInfo();
        } else if (lowerMessage.includes('help') || lowerMessage.includes('support')) {
            this.handleSupport();
        } else {
            // Default response with helpful options
            setTimeout(() => {
                this.addMessage('bot', `I'd be happy to help you with that! 😊

Here are some things I can assist you with:`, true);
                
                this.showQuickReplies([
                    { text: '💰 Selling timeshares', action: () => this.handleSellFlow() },
                    { text: '🏖️ Renting timeshares', action: () => this.handleRentFlow() },
                    { text: '💳 Pricing plans', action: () => this.handlePricingFlow() },
                    { text: '📞 Contact support', action: () => this.handleContactInfo() }
                ]);
            }, 1000);
        }
    }

    handleContactInfo() {
        setTimeout(() => {
            this.addMessage('bot', `I'd love to connect you with our team! 📞

**Contact Options:**
• **Email:** support@selfservetimeshare.com
• **Phone:** Available with Premium/Unlimited plans
• **Live Chat:** Right here with me!
• **Help Center:** Comprehensive FAQ and guides

**Response Times:**
• Chat: Instant (that's me!)
• Email: Within 4 hours
• Phone: Same day callback

What's the best way for our team to reach you?`, true);
            
            this.showQuickReplies([
                { text: '📧 Email me', action: () => this.handleEmailContact() },
                { text: '📞 Schedule call', action: () => this.handlePhoneContact() },
                { text: '💬 Keep chatting', action: () => this.handleContinueChat() }
            ]);
        }, 1000);
    }

    handleEmailContact() {
        this.hideQuickReplies();
        this.addMessage('user', '📧 Email me');
        
        setTimeout(() => {
            this.addMessage('bot', `Perfect! I'll make sure our team reaches out to you. 📧

Please provide your email address and I'll have a specialist contact you within 4 hours with:
• Personalized recommendations for your situation
• Detailed platform walkthrough
• Answers to any specific questions
• Special getting-started bonus

What's your email address?`, true);
        }, 1000);
    }
}

// Initialize chatbot when page loads
document.addEventListener('DOMContentLoaded', function() {
    window.chatbot = new TimeshareChatbot();
});

