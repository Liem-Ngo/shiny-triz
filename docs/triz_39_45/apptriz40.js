/**
 * TRIZ Principles Explorer Application
 * 
 * This application allows users to search for and explore the 40 TRIZ principles
 * and their examples across different industries.
 */

// Global variables
let trizPrinciples = [];
let industryExamples = {};
let industryPrinciples = {};
let selectedPrinciple = null;
let currentIndustry = 'general';

// Available industries
const INDUSTRIES = [
    { id: 'general', name: 'General' },
    { id: 'software', name: 'Software Engineering' },
    { id: 'education', name: 'Education' },
    { id: 'design', name: 'Design' },
    { id: 'business', name: 'Bussiness' },
    { id: 'finance', name: 'Finance' },
    { id: 'chemical', name: 'Chemical Engineering' },
    { id: 'social', name: 'Social' },
    { id: 'human', name: 'Human Factors and Ergonomics' },
    { id: 'microelectronics', name: 'Microelectronics' },
    { id: 'customer', name: 'Customer Satisfaction Enhancement' }
    // Add more industries as they become available
];

// DOM Elements
const principleSelect = document.getElementById('principle-select');
const industrySelect = document.getElementById('industry-select');
const principleContainer = document.getElementById('principle-container');
const principleTitle = document.getElementById('principle-title');
const principleContent = document.getElementById('principle-content');
const currentIndustrySpan = document.getElementById('current-industry');
const loadingSpinner = document.getElementById('loading-spinner');
const noResults = document.getElementById('no-results');
const introductionText = document.getElementById('introduction-text');
const backToTop = document.getElementById('back-to-top');

// Load data when DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize the application
    init();
});

/**
 * Initialize the application
 */
async function init() {
    // Show loading spinner during initialization
    loadingSpinner.style.display = 'block';
    
    try {
        // Set up event listeners
        setupEventListeners();
        
        // Load principles data
        await loadPrinciplesData();
        
        // Load industry examples
        await loadIndustryPrinciples();
        
        // Populate principle select dropdown
        populatePrincipleSelect();
        
        // Populate industry select dropdown
        populateIndustrySelect();
        
        // Hide loading spinner
        loadingSpinner.style.display = 'none';
        
    } catch (error) {
        console.error('Error initializing application:', error);
        alert('Could not load TRIZ principles data. Please refresh the page and try again.');
        loadingSpinner.style.display = 'none';
    }
}

/**
 * Set up event listeners for UI elements
 */
function setupEventListeners() {
    // Principle select change
    principleSelect.addEventListener('change', (e) => {
        const principleId = parseInt(e.target.value);
        
        if (principleId) {
            console.log('Principle changed to:', principleId);
            selectPrinciple(principleId);
        }
    });
    
    // Industry select change
    industrySelect.addEventListener('change', (e) => {
        console.log('Industry changed to:', e.target.value);
        
        if (selectedPrinciple) {
            changeIndustry(e.target.value);
        } else {
            console.log('No principle selected yet');
        }
    });
    
    // Back to top button
    backToTop.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    
    // Show/hide back to top button on scroll
    window.addEventListener('scroll', () => {
        if (window.scrollY > 300) {
            backToTop.classList.add('visible');
        } else {
            backToTop.classList.remove('visible');
        }
    });
}

/**
 * Load principles data from the JSON file
 */
async function loadPrinciplesData() {
    try {
        console.log('Loading principles data...');
        const response = await fetch('data/principles.json');
        trizPrinciples = await response.json();
        console.log('Principles data loaded successfully:', trizPrinciples.length, 'principles');
    } catch (error) {
        console.error('Error loading principles data:', error);
        
        // Fallback to minimal data to allow app to function
        trizPrinciples = [
            {
                id: 1,
                name: "Segmentation",
                descriptions: [
                    {
                        text: "Divide an object into independent parts.",
                        examples: ["Example 1", "Example 2"]
                    }
                ]
            },
            {
                id: 2,
                name: "Taking Out",
                descriptions: [
                    {
                        text: "Separate an interfering part or property from an object.",
                        examples: ["Example 1", "Example 2"]
                    }
                ]
            }
        ];
    }
}

/**
 * Populate the principle select dropdown with all 40 principles
 */
function populatePrincipleSelect() {
    // Sort principles by ID to ensure they appear in correct order
    const sortedPrinciples = [...trizPrinciples].sort((a, b) => a.id - b.id);
    
    console.log('Populating principle select with', sortedPrinciples.length, 'principles');
    
    // Add default option
    const defaultOption = document.createElement('option');
    defaultOption.value = "";
    defaultOption.textContent = "Select a principle (1-40)";
    defaultOption.disabled = true;
    defaultOption.selected = true;
    principleSelect.appendChild(defaultOption);
    
    // Generate options for each principle
    sortedPrinciples.forEach(principle => {
        const option = document.createElement('option');
        option.value = principle.id;
        option.textContent = `${principle.id}. ${principle.name}`;
        principleSelect.appendChild(option);
    });
    
    console.log('Principle select populated');
}

/**
 * Load industry-specific principles from individual JSON files
 */
async function loadIndustryPrinciples() {
    console.log('Loading industry-specific principles...');
    
    // Initialize the industry principles object
    industryPrinciples = {};
    industryExamples = {};
       
    // Load individual industry files with Promise.all
    const industryPromises = INDUSTRIES
        .filter(industry => industry.id !== 'general')
        .map(industry => {
            return fetch(`data/principles_${industry.id}.json`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Failed to load ${industry.id} principles`);
                    }
                    return response.json();
                })
                .then(data => {
                    // Store the industry principles data
                    industryPrinciples[industry.id] = data;
                    
                    // Also process for the examples format we need
                    if (data.principles) {
                        industryExamples[industry.id] = {};
                        data.principles.forEach(principle => {
                            industryExamples[industry.id][principle.id] = principle.examples;
                        });
                    }
                })
                .catch(error => {
                    console.error(`Error loading ${industry.id} principles:`, error);
                    // If loading fails, set empty to avoid errors later
                    industryPrinciples[industry.id] = { principles: [] };
                });
        });
    
    // Wait for all industry principles to load
    await Promise.all(industryPromises);
    console.log('All industry principles loaded');
}

/**
 * Populate the industry select dropdown with available industries
 */
function populateIndustrySelect() {
    // Clear current options
    industrySelect.innerHTML = '';
    
    console.log('Populating industry select...');
    
    // Add each industry as an option
    INDUSTRIES.forEach(industry => {
        const option = document.createElement('option');
        option.value = industry.id;
        option.textContent = industry.name;
        
        // Set the general option as default
        if (industry.id === 'general') {
            option.selected = true;
        }
        
        industrySelect.appendChild(option);
    });
    
    // Initially disable the industry select until a principle is chosen
    industrySelect.disabled = true;
    
    console.log('Industry select populated');
}

/**
 * Get the human-readable name for an industry
 */
function getIndustryName(industryId) {
    const industry = INDUSTRIES.find(i => i.id === industryId);
    return industry ? industry.name : industryId.charAt(0).toUpperCase() + industryId.slice(1);
}

/**
 * Change the current industry and update the display
 */
function changeIndustry(industryId) {
    currentIndustry = industryId;
    
    // Update the displayed industry name
    currentIndustrySpan.textContent = getIndustryName(currentIndustry);
    
    // Update the displayed content with the new industry
    displayPrincipleContent();
    
    console.log('Changed to industry:', industryId);
}

/**
 * Select a principle and display its details
 */
function selectPrinciple(principleId) {
    // Find the principle by ID
    selectedPrinciple = trizPrinciples.find(p => p.id === principleId);
    
    if (!selectedPrinciple) {
        noResults.style.display = 'block';
        principleContainer.style.display = 'none';
        return;
    }
    
    // Reset to general industry
    currentIndustry = 'general';
    industrySelect.value = 'general';
    currentIndustrySpan.textContent = getIndustryName('general');
    
    // Enable industry select
    industrySelect.disabled = false;
    
    // Hide introduction and no results
    introductionText.style.display = 'none';
    noResults.style.display = 'none';
    
    // Show loading spinner
    loadingSpinner.style.display = 'block';
    principleContainer.style.display = 'none';
    
    // Simulate loading delay
    setTimeout(() => {
        loadingSpinner.style.display = 'none';
        
        // Update principle title
        principleTitle.textContent = `Principle ${selectedPrinciple.id}: ${selectedPrinciple.name}`;
        
        // Display principle content
        displayPrincipleContent();
        
        // Show principle container
        principleContainer.style.display = 'block';
        
        // Scroll to principle container
        principleContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 300);
}

/**
 * Display principle content based on selected principle and industry
 */
function displayPrincipleContent() {
    if (!selectedPrinciple) return;
    
    let html = '';
    
    // Display principle descriptions (general examples)
    if (currentIndustry === 'general') {
        selectedPrinciple.descriptions.forEach((description, index) => {
            html += `
                <div class="principle-description">
                    <p>${description.text}</p>
                </div>
                <div class="principle-examples">
                    <h5>Examples</h5>
                    <ul>
            `;
            
            description.examples.forEach(example => {
                html += `<li>${example}</li>`;
            });
            
            html += `
                    </ul>
                </div>
            `;
            
            // Add separator if not the last description
            if (index < selectedPrinciple.descriptions.length - 1) {
                html += `<hr class="my-4">`;
            }
        });
    }
    // Display industry-specific examples
    else {
        // Check if industry examples exist for this principle
        const industryPrincipleExamples = industryExamples[currentIndustry] && 
                                        industryExamples[currentIndustry][selectedPrinciple.id];
        
        if (industryPrincipleExamples && industryPrincipleExamples.length > 0) {
            // Add principle description first
            if (selectedPrinciple.descriptions && selectedPrinciple.descriptions.length > 0) {
                html += `
                    <div class="principle-description">
                        <p>${selectedPrinciple.descriptions[0].text}</p>
                    </div>
                `;
            }
            
            // Add industry examples
            industryPrincipleExamples.forEach((exampleGroup, groupIndex) => {
                html += `
                    <div class="principle-examples">
                        <h5>${getIndustryName(currentIndustry)} Examples</h5>
                        <ul>
                `;
                
                exampleGroup.forEach(example => {
                    html += `<li>${example}</li>`;
                });
                
                html += `
                        </ul>
                    </div>
                `;
                
                // Add separator if not the last example group
                if (groupIndex < industryPrincipleExamples.length - 1) {
                    html += `<hr class="my-3">`;
                }
            });
        } else {
            // If no industry examples, show message and general examples
            html += `
                <div class="alert alert-info">
                    <i class="fas fa-info-circle me-2"></i>
                    No specific examples available for ${getIndustryName(currentIndustry)} industry.
                    Showing general examples instead.
                </div>
            `;
            
            // Show general examples
            selectedPrinciple.descriptions.forEach((description, index) => {
                html += `
                    <div class="principle-description">
                        <p>${description.text}</p>
                    </div>
                    <div class="principle-examples">
                        <h5>General Examples</h5>
                        <ul>
                `;
                
                description.examples.forEach(example => {
                    html += `<li>${example}</li>`;
                });
                
                html += `
                        </ul>
                    </div>
                `;
                
                // Add separator if not the last description
                if (index < selectedPrinciple.descriptions.length - 1) {
                    html += `<hr class="my-4">`;
                }
            });
        }
    }
    
    // Add "change industry" prompt if viewing general examples
    if (currentIndustry === 'general') {
        html += `
            <div class="mt-4 text-center">
                <p class="text-muted">
                    <i class="fas fa-lightbulb me-2"></i>
                    Select an industry from the dropdown to see industry-specific examples.
                </p>
            </div>
        `;
    }
    
    principleContent.innerHTML = html;
}

// Console logging to check initialization
console.log('TRIZ Principles Explorer script loaded');