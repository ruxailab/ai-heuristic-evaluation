import { httpsCallable } from "firebase/functions";
import { getFunctions } from "firebase/functions";

class AIHeuristicEvaluationClient {
  constructor() {
    this.functions = getFunctions();
  }

  async evaluateImage(imageData, studyId, questionId) {
    try {
      const evaluateFunction = httpsCallable(this.functions, "evaluateHeuristicAI");
      const result = await evaluateFunction({ imageData, studyId, questionId });
      return result.data;
    } catch (error) {
      console.error("Error evaluating heuristic:", error);
      throw error;
    }
  }

  async detectUIElements(imageData) {
    try {
      const detectFunction = httpsCallable(this.functions, "detectUIElements");
      const result = await detectFunction({ imageData });
      return result.data;
    } catch (error) {
      console.error("Error detecting UI elements:", error);
      throw error;
    }
  }

  async getHeuristicsMetadata() {
    try {
      const metadataFunction = httpsCallable(this.functions, "getHeuristicsMetadata");
      const result = await metadataFunction({});
      return result.data;
    } catch (error) {
      console.error("Error fetching heuristics metadata:", error);
      throw error;
    }
  }

  async getKnowledgeBaseStats() {
    try {
      const statsFunction = httpsCallable(this.functions, "getKnowledgeBaseStats");
      const result = await statsFunction({});
      return result.data;
    } catch (error) {
      console.error("Error fetching knowledge base stats:", error);
      throw error;
    }
  }
}

export default AIHeuristicEvaluationClient;
