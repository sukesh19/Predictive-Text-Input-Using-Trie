#include <iostream>
#include <unordered_map>
#include <vector>
#include <string>
#include <algorithm>
#include <fstream>
#include <sstream>
#include <chrono>
#include <cstdlib>
#include <ctime>

// TrieNode class for storing character nodes
class TrieNode {
public:
    std::unordered_map<char, TrieNode*> children;
    bool isEndOfWord;
    int frequency;           // ML element: tracks word usage frequency
    std::string word;        // Store complete word at end nodes
    
    TrieNode() : isEndOfWord(false), frequency(0) {}
};

// Main Predictive Text System with ML capabilities
class PredictiveTextSystem {
private:
    TrieNode* root;
    std::vector<std::pair<std::string, int>> suggestions;
    
    // Helper function to convert string to lowercase
    std::string toLower(const std::string& str) {
        std::string result = str;
        std::transform(result.begin(), result.end(), result.begin(), ::tolower);
        return result;
    }
    
    // Find the node corresponding to a prefix
    TrieNode* findPrefixNode(const std::string& prefix) {
        TrieNode* current = root;
        for (char ch : prefix) {
            if (current->children.find(ch) == current->children.end()) {
                return nullptr;
            }
            current = current->children[ch];
        }
        return current;
    }
    
    // Recursively collect all words with given prefix
    void collectSuggestions(TrieNode* node, const std::string& prefix) {
        if (node->isEndOfWord) {
            suggestions.push_back({node->word, node->frequency});
        }
        
        for (auto& pair : node->children) {
            collectSuggestions(pair.second, prefix + pair.first);
        }
    }
    
    // Search for exact word in trie
    bool search(const std::string& word) {
        TrieNode* current = root;
        std::string lowerWord = toLower(word);
        
        for (char ch : lowerWord) {
            if (current->children.find(ch) == current->children.end()) {
                return false;
            }
            current = current->children[ch];
        }
        
        return current->isEndOfWord;
    }
    
    // Find correction candidates using edit distance
    void findCandidates(TrieNode* node, const std::string& current, const std::string& target, 
                       std::vector<std::pair<std::string, int>>& candidates, int editDistance, int maxDistance) {
        if (editDistance > maxDistance) return;
        
        if (node->isEndOfWord && editDistance <= maxDistance) {
            candidates.push_back({node->word, node->frequency - editDistance * 10}); // Penalize edit distance
        }
        
        for (auto& pair : node->children) {
            char ch = pair.first;
            TrieNode* child = pair.second;
            
            // Try different edit operations
            findCandidates(child, current + ch, target, candidates, editDistance + 1, maxDistance); // Insertion
            
            if (!target.empty()) {
                if (current.length() < target.length() && target[current.length()] == ch) {
                    findCandidates(child, current + ch, target, candidates, editDistance, maxDistance); // Match
                } else {
                    findCandidates(child, current + ch, target, candidates, editDistance + 1, maxDistance); // Substitution
                }
            }
        }
    }
    
    // Split text into individual words
    std::vector<std::string> splitIntoWords(const std::string& text) {
        std::vector<std::string> words;
        std::istringstream iss(text);
        std::string word;
        while (iss >> word) {
            // Remove punctuation
            word.erase(std::remove_if(word.begin(), word.end(), 
                      [](char c) { return !std::isalnum(c); }), word.end());
            if (!word.empty()) {
                words.push_back(word);
            }
        }
        return words;
    }
    
    // Load common English words with initial frequencies
    void loadCommonWords() {
        std::vector<std::pair<std::string, int>> commonWords = {
            {"the", 100}, {"and", 90}, {"to", 85}, {"of", 80}, {"a", 75},
            {"in", 70}, {"is", 65}, {"it", 60}, {"you", 55}, {"that", 50},
            {"he", 45}, {"was", 45}, {"for", 40}, {"on", 40}, {"are", 35},
            {"as", 35}, {"with", 30}, {"his", 30}, {"they", 25}, {"i", 25},
            {"at", 20}, {"be", 20}, {"this", 20}, {"have", 18}, {"from", 18},
            {"or", 15}, {"one", 15}, {"had", 15}, {"by", 12}, {"word", 12},
            {"but", 10}, {"not", 10}, {"what", 10}, {"all", 8}, {"were", 8},
            {"would", 7}, {"there", 7}, {"we", 6}, {"when", 6}, {"your", 5},
            {"can", 12}, {"said", 11}, {"each", 9}, {"which", 9}, {"she", 8},
            {"do", 15}, {"how", 12}, {"their", 10}, {"if", 14}, {"will", 13},
            {"up", 11}, {"other", 8}, {"about", 7}, {"out", 10}, {"many", 6},
            {"then", 9}, {"them", 8}, {"these", 6}, {"so", 12}, {"some", 7},
            {"her", 9}, {"would", 7}, {"make", 8}, {"like", 9}, {"into", 6},
            {"him", 7}, {"time", 8}, {"has", 9}, {"two", 6}, {"more", 7},
            {"go", 8}, {"no", 9}, {"way", 6}, {"could", 6}, {"my", 10},
            {"than", 6}, {"first", 5}, {"been", 6}, {"call", 4}, {"who", 7},
            {"its", 5}, {"now", 8}, {"find", 5}, {"long", 4}, {"down", 5},
            {"day", 6}, {"did", 6}, {"get", 8}, {"come", 5}, {"made", 5},
            {"may", 4}, {"part", 4}, {"over", 5}, {"new", 6}, {"sound", 3},
            {"take", 6}, {"only", 5}, {"little", 4}, {"work", 5}, {"know", 7}
        };
        
        for (const auto& pair : commonWords) {
            insertWord(pair.first, pair.second);
        }
    }
    
    // Save trie to file recursively
    void saveTrieToFile(TrieNode* node, const std::string& prefix, std::ofstream& file) {
        if (node->isEndOfWord) {
            file << node->word << " " << node->frequency << std::endl;
        }
        
        for (auto& pair : node->children) {
            saveTrieToFile(pair.second, prefix + pair.first, file);
        }
    }
    
    // Calculate system statistics recursively
    void calculateStats(TrieNode* node, int& totalWords, int& totalFrequency) {
        if (node->isEndOfWord) {
            totalWords++;
            totalFrequency += node->frequency;
        }
        
        for (auto& pair : node->children) {
            calculateStats(pair.second, totalWords, totalFrequency);
        }
    }
    
    // Delete trie to prevent memory leaks
    void deleteTrie(TrieNode* node) {
        for (auto& pair : node->children) {
            deleteTrie(pair.second);
        }
        delete node;
    }
    
public:
    PredictiveTextSystem() {
        root = new TrieNode();
        loadCommonWords(); // Initialize with common vocabulary
    }
    
    ~PredictiveTextSystem() {
        deleteTrie(root);
    }
    
    // Insert word with frequency tracking (Learning Component)
    void insertWord(const std::string& word, int frequencyIncrease = 1) {
        if (word.empty()) return;
        
        TrieNode* current = root;
        
        // Convert to lowercase for consistency
        std::string lowerWord = toLower(word);
        
        for (char ch : lowerWord) {
            if (current->children.find(ch) == current->children.end()) {
                current->children[ch] = new TrieNode();
            }
            current = current->children[ch];
        }
        
        current->isEndOfWord = true;
        current->frequency += frequencyIncrease;  // ML: Learn from usage
        current->word = lowerWord;
    }
    
    // Smart search with learning-based ranking
    std::vector<std::string> getSuggestions(const std::string& prefix, int maxSuggestions = 5) {
        suggestions.clear();
        
        if (prefix.empty()) return {};
        
        std::string lowerPrefix = toLower(prefix);
        TrieNode* prefixNode = findPrefixNode(lowerPrefix);
        
        if (!prefixNode) return {};
        
        // Collect all words with this prefix
        collectSuggestions(prefixNode, lowerPrefix);
        
        // Sort by frequency (ML element) then alphabetically
        std::sort(suggestions.begin(), suggestions.end(), 
                 [](const std::pair<std::string, int>& a, const std::pair<std::string, int>& b) {
                     if (a.second != b.second) {
                         return a.second > b.second; // Higher frequency first
                     }
                     return a.first < b.first; // Alphabetical for same frequency
                 });
        
        // Extract top suggestions
        std::vector<std::string> result;
        for (int i = 0; i < std::min(maxSuggestions, (int)suggestions.size()); i++) {
            result.push_back(suggestions[i].first);
        }
        
        return result;
    }
    
    // Learn from user selection (Reinforcement Learning)
    void userSelectedWord(const std::string& word) {
        insertWord(word, 5); // Boost frequency significantly for user choices
        std::cout << "Learning: Increased priority for '" << word << "'" << std::endl;
    }
    
    // Predict next word based on context (Advanced ML feature)
    std::vector<std::string> predictNextWord(const std::string& context) {
        std::vector<std::string> contextWords = splitIntoWords(context);
        if (contextWords.empty()) return {};
        
        // Simple bigram prediction: find words that commonly follow the last word
        std::string lastWord = toLower(contextWords.back());
        std::vector<std::string> predictions;
        
        // Enhanced prediction based on common word patterns
        if (lastWord == "i" || lastWord == "you" || lastWord == "we" || lastWord == "they") {
            std::vector<std::string> verbSuggestions = {"am", "are", "will", "can", "have", "want", "need"};
            for (const auto& verb : verbSuggestions) {
                if (search(verb)) {
                    predictions.push_back(verb);
                }
            }
        } else if (lastWord == "the" || lastWord == "a" || lastWord == "an") {
            // Suggest common nouns
            std::vector<char> commonStarters = {'c', 'b', 'f', 'm', 'p', 's', 'w', 'h'};
            for (char starter : commonStarters) {
                auto wordSuggestions = getSuggestions(std::string(1, starter), 2);
                predictions.insert(predictions.end(), wordSuggestions.begin(), wordSuggestions.end());
            }
        } else {
            // General high-frequency words
            std::vector<char> commonStarters = {'t', 'a', 'i', 'o', 'h', 'w'};
            for (char starter : commonStarters) {
                auto wordSuggestions = getSuggestions(std::string(1, starter), 2);
                predictions.insert(predictions.end(), wordSuggestions.begin(), wordSuggestions.end());
            }
        }
        
        // Remove duplicates and limit results
        std::sort(predictions.begin(), predictions.end());
        predictions.erase(std::unique(predictions.begin(), predictions.end()), predictions.end());
        
        if (predictions.size() > 6) {
            predictions.resize(6);
        }
        
        return predictions;
    }
    
    // Auto-correct with learning (ML-based correction)
    std::string autoCorrect(const std::string& word) {
        if (search(word)) return word; // Word is correct
        
        // Find closest words using edit distance
        std::vector<std::pair<std::string, int>> candidates;
        findCandidates(root, "", toLower(word), candidates, 0, 2); // Max edit distance of 2
        
        if (candidates.empty()) return word;
        
        // Sort by frequency and edit distance
        std::sort(candidates.begin(), candidates.end(), 
                 [](const std::pair<std::string, int>& a, const std::pair<std::string, int>& b) {
                     return a.second > b.second;
                 });
        
        return candidates[0].first;
    }
    
    // Save learned patterns to file
    void saveModel(const std::string& filename) {
        std::ofstream file(filename);
        if (file.is_open()) {
            saveTrieToFile(root, "", file);
            file.close();
            std::cout << "Model saved to " << filename << std::endl;
        } else {
            std::cout << "Error: Could not save model to " << filename << std::endl;
        }
    }
    
    // Load learned patterns from file
    void loadModel(const std::string& filename) {
        std::ifstream file(filename);
        if (file.is_open()) {
            std::string line;
            while (std::getline(file, line)) {
                std::istringstream iss(line);
                std::string word;
                int frequency;
                if (iss >> word >> frequency) {
                    insertWord(word, frequency);
                }
            }
            file.close();
            std::cout << "Model loaded from " << filename << std::endl;
        } else {
            std::cout << "Could not load model from " << filename << std::endl;
        }
    }
    
    // Display system statistics
    void displayStats() {
        int totalWords = 0;
        int totalFrequency = 0;
        calculateStats(root, totalWords, totalFrequency);
        
        std::cout << "\n=== Predictive Text System Stats ===" << std::endl;
        std::cout << "Total unique words: " << totalWords << std::endl;
        std::cout << "Total usage frequency: " << totalFrequency << std::endl;
        std::cout << "Average usage per word: " << (totalWords > 0 ? (double)totalFrequency/totalWords : 0) << std::endl;
        std::cout << "====================================" << std::endl;
    }
    
    // Add multiple words from text (for training)
    void trainFromText(const std::string& text) {
        std::vector<std::string> words = splitIntoWords(text);
        std::cout << "Training from " << words.size() << " words..." << std::endl;
        
        for (const auto& word : words) {
            insertWord(word, 1);
        }
        
        std::cout << "Training completed!" << std::endl;
    }
};

// Interactive Demo Class
class PredictiveTextDemo {
private:
    PredictiveTextSystem textSystem;
    
public:
    void runDemo() {
        std::cout << "=== Predictive Text System with Machine Learning ===" << std::endl;
        std::cout << "This system learns from your usage patterns!" << std::endl;
        std::cout << "\nCommands:" << std::endl;
        std::cout << "  - Type any prefix to get autocomplete suggestions" << std::endl;
        std::cout << "  - 'select <word>' - Learn from your word choice" << std::endl;
        std::cout << "  - 'correct <word>' - Get auto-correction suggestions" << std::endl;
        std::cout << "  - 'predict <context>' - Predict next word based on context" << std::endl;
        std::cout << "  - 'train <text>' - Train system with custom text" << std::endl;
        std::cout << "  - 'stats' - View system statistics" << std::endl;
        std::cout << "  - 'save' / 'load' - Persist learning to file" << std::endl;
        std::cout << "  - 'demo' - Run automated demonstration" << std::endl;
        std::cout << "  - 'quit' - Exit the program" << std::endl;
        std::cout << "======================================================" << std::endl;
        
        std::string input;
        while (true) {
            std::cout << "\n> ";
            std::getline(std::cin, input);
            
            if (input.empty()) continue;
            
            if (input == "quit") {
                std::cout << "Thank you for using Predictive Text System!" << std::endl;
                break;
            } else if (input == "stats") {
                textSystem.displayStats();
            } else if (input == "save") {
                textSystem.saveModel("learned_model.txt");
            } else if (input == "load") {
                textSystem.loadModel("learned_model.txt");
            } else if (input == "demo") {
                runAutomatedDemo();
            } else if (input.substr(0, 7) == "select ") {
                std::string word = input.substr(7);
                textSystem.userSelectedWord(word);
            } else if (input.substr(0, 8) == "correct ") {
                std::string word = input.substr(8);
                std::string corrected = textSystem.autoCorrect(word);
                std::cout << "Auto-correction: '" << word << "' -> '" << corrected << "'" << std::endl;
                if (corrected != word) {
                    std::cout << "Learning from correction..." << std::endl;
                    textSystem.userSelectedWord(corrected);
                }
            } else if (input.substr(0, 8) == "predict ") {
                std::string context = input.substr(8);
                auto predictions = textSystem.predictNextWord(context);
                std::cout << "Next word predictions for '" << context << "': ";
                if (predictions.empty()) {
                    std::cout << "No predictions available";
                } else {
                    for (size_t i = 0; i < predictions.size(); i++) {
                        std::cout << predictions[i];
                        if (i < predictions.size() - 1) std::cout << ", ";
                    }
                }
                std::cout << std::endl;
            } else if (input.substr(0, 6) == "train ") {
                std::string text = input.substr(6);
                textSystem.trainFromText(text);
            } else {
                // Get autocomplete suggestions
                auto suggestions = textSystem.getSuggestions(input, 8);
                
                if (suggestions.empty()) {
                    std::cout << "No suggestions found for '" << input << "'" << std::endl;
                    
                    // Try auto-correction
                    std::string corrected = textSystem.autoCorrect(input);
                    if (corrected != input) {
                        std::cout << "Did you mean: '" << corrected << "'?" << std::endl;
                    }
                } else {
                    std::cout << "Suggestions for '" << input << "': ";
                    for (size_t i = 0; i < suggestions.size(); i++) {
                        std::cout << suggestions[i];
                        if (i < suggestions.size() - 1) std::cout << ", ";
                    }
                    std::cout << std::endl;
                }
            }
        }
    }
    
    void runAutomatedDemo() {
        std::cout << "\n=== Automated Demo ===" << std::endl;
        
        // Demo 1: Basic autocomplete
        std::cout << "\n1. Basic Autocomplete:" << std::endl;
        std::vector<std::string> prefixes = {"th", "com", "wor", "app"};
        for (const auto& prefix : prefixes) {
            auto suggestions = textSystem.getSuggestions(prefix, 5);
            std::cout << "   '" << prefix << "' -> ";
            for (size_t i = 0; i < suggestions.size(); i++) {
                std::cout << suggestions[i];
                if (i < suggestions.size() - 1) std::cout << ", ";
            }
            std::cout << std::endl;
        }
        
        // Demo 2: Learning from user selection
        std::cout << "\n2. Learning from Selection:" << std::endl;
        std::cout << "   Before learning: ";
        auto before = textSystem.getSuggestions("pro", 3);
        for (size_t i = 0; i < before.size(); i++) {
            std::cout << before[i];
            if (i < before.size() - 1) std::cout << ", ";
        }
        std::cout << std::endl;
        
        textSystem.userSelectedWord("programming");
        textSystem.userSelectedWord("programming");
        textSystem.userSelectedWord("program");
        
        std::cout << "   After learning: ";
        auto after = textSystem.getSuggestions("pro", 3);
        for (size_t i = 0; i < after.size(); i++) {
            std::cout << after[i];
            if (i < after.size() - 1) std::cout << ", ";
        }
        std::cout << std::endl;
        
        // Demo 3: Auto-correction
        std::cout << "\n3. Auto-correction:" << std::endl;
        std::vector<std::string> typos = {"teh", "recieve", "seperate", "occured"};
        for (const auto& typo : typos) {
            std::string corrected = textSystem.autoCorrect(typo);
            std::cout << "   '" << typo << "' -> '" << corrected << "'" << std::endl;
        }
        
        // Demo 4: Context prediction
        std::cout << "\n4. Context Prediction:" << std::endl;
        std::vector<std::string> contexts = {"I am", "The quick", "We will", "She can"};
        for (const auto& context : contexts) {
            auto predictions = textSystem.predictNextWord(context);
            std::cout << "   '" << context << "' -> ";
            for (size_t i = 0; i < std::min((size_t)3, predictions.size()); i++) {
                std::cout << predictions[i];
                if (i < std::min((size_t)3, predictions.size()) - 1) std::cout << ", ";
            }
            std::cout << std::endl;
        }
        
        std::cout << "\nDemo completed!" << std::endl;
    }
    
    void runBenchmark() {
        std::cout << "\n=== Performance Benchmark ===" << std::endl;
        
        // Add sample data
        std::vector<std::string> sampleWords = {
            "algorithm", "application", "computer", "programming", "development",
            "artificial", "intelligence", "machine", "learning", "technology",
            "software", "hardware", "network", "database", "security",
            "framework", "interface", "structure", "function", "variable",
            "optimization", "implementation", "documentation", "debugging", "testing"
        };
        
        auto start = std::chrono::high_resolution_clock::now();
        
        // Insert words
        for (const auto& word : sampleWords) {
            textSystem.insertWord(word, rand() % 50 + 1);
        }
        
        // Perform searches
        int operations = 1000;
        for (int i = 0; i < operations; i++) {
            std::string prefix = sampleWords[rand() % sampleWords.size()].substr(0, rand() % 4 + 1);
            textSystem.getSuggestions(prefix);
        }
        
        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
        
        std::cout << "Benchmark Results:" << std::endl;
        std::cout << "- Operations performed: " << operations + sampleWords.size() << std::endl;
        std::cout << "- Total time: " << duration.count() << " microseconds" << std::endl;
        std::cout << "- Average time per operation: " << (double)duration.count() / (operations + sampleWords.size()) << " microseconds" << std::endl;
        
        textSystem.displayStats();
    }
};

// Main function
int main() {
    srand(time(nullptr));
    
    PredictiveTextDemo demo;
    
    std::cout << "=== Predictive Text System with Trie & Machine Learning ===" << std::endl;
    std::cout << "Choose mode:" << std::endl;
    std::cout << "1. Interactive Demo" << std::endl;
    std::cout << "2. Performance Benchmark" << std::endl;
    std::cout << "3. Quick Demo" << std::endl;
    std::cout << "Enter choice (1, 2, or 3): ";
    
    int choice;
    std::cin >> choice;
    std::cin.ignore(); // Clear the newline
    
    switch(choice) {
        case 1:
            demo.runDemo();
            break;
        case 2:
            demo.runBenchmark();
            break;
        case 3:
            demo.runAutomatedDemo();
            break;
        default:
            std::cout << "Invalid choice! Running interactive demo..." << std::endl;
            demo.runDemo();
            break;
    }
    
    return 0;
}
