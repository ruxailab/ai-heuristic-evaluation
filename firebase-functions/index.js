import { onCall, HttpsError } from "firebase-functions/v2/https";
import { logger } from "firebase-functions";
import * as admin from "firebase-admin";

admin.initializeApp();

const AI_SERVICE_URL = process.env.AI_SERVICE_URL || "http://localhost:8000";

export const evaluateHeuristicAI = onCall(async (request) => {
  try {
    const { imageData, studyId, questionId } = request.data;

    if (!imageData) {
      throw new HttpsError("invalid-argument", "Image data is required");
    }

    logger.info(`Starting AI heuristic evaluation for study ${studyId}`);

    const base64Image = imageData.replace(/^data:image\/\w+;base64,/, "");
    const imageBuffer = Buffer.from(base64Image, "base64");

    const formData = new FormData();
    formData.append("image", new Blob([imageBuffer]), "screenshot.png");

    const response = await fetch(`${AI_SERVICE_URL}/api/v1/evaluation/evaluate`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`AI service returned ${response.status}`);
    }

    const result = await response.json();

    if (!result.success) {
      throw new Error(result.error || "Evaluation failed");
    }

    const db = admin.firestore();

    const evaluationData = {
      studyId,
      questionId,
      aiEvaluation: result.data,
      createdAt: admin.firestore.FieldValue.serverTimestamp(),
      source: "ai_heuristic",
      version: "1.0.0"
    };

    const docRef = await db.collection("ai_heuristic_evaluations").add(evaluationData);

    logger.info(`AI evaluation complete: ${result.data.overall_score} score`);

    return {
      success: true,
      evaluationId: docRef.id,
      data: result.data
    };

  } catch (error) {
    logger.error("Error in evaluateHeuristicAI:", error);
    throw new HttpsError("internal", error.message);
  }
});

export const detectUIElements = onCall(async (request) => {
  try {
    const { imageData } = request.data;

    if (!imageData) {
      throw new HttpsError("invalid-argument", "Image data is required");
    }

    logger.info("Starting UI element detection");

    const base64Image = imageData.replace(/^data:image\/\w+;base64,/, "");
    const imageBuffer = Buffer.from(base64Image, "base64");

    const formData = new FormData();
    formData.append("image", new Blob([imageBuffer]), "screenshot.png");

    const response = await fetch(`${AI_SERVICE_URL}/api/v1/heuristic/analyze`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`AI service returned ${response.status}`);
    }

    const result = await response.json();

    if (!result.success) {
      throw new Error(result.error || "Detection failed");
    }

    logger.info(`Detection complete: ${result.data.summary.total_elements} elements found`);

    return {
      success: true,
      data: result.data
    };

  } catch (error) {
    logger.error("Error in detectUIElements:", error);
    throw new HttpsError("internal", error.message);
  }
});

export const getHeuristicsMetadata = onCall(async (request) => {
  try {
    logger.info("Fetching heuristics metadata");

    const response = await fetch(`${AI_SERVICE_URL}/api/v1/evaluation/heuristics`);

    if (!response.ok) {
      throw new Error(`AI service returned ${response.status}`);
    }

    const result = await response.json();

    if (!result.success) {
      throw new Error(result.error || "Failed to fetch heuristics");
    }

    return {
      success: true,
      data: result.data
    };

  } catch (error) {
    logger.error("Error in getHeuristicsMetadata:", error);
    throw new HttpsError("internal", error.message);
  }
});

export const getKnowledgeBaseStats = onCall(async (request) => {
  try {
    logger.info("Fetching knowledge base stats");

    const response = await fetch(`${AI_SERVICE_URL}/api/v1/evaluation/knowledge-base/stats`);

    if (!response.ok) {
      throw new Error(`AI service returned ${response.status}`);
    }

    const result = await response.json();

    if (!result.success) {
      throw new Error(result.error || "Failed to fetch knowledge base stats");
    }

    return {
      success: true,
      data: result.data
    };

  } catch (error) {
    logger.error("Error in getKnowledgeBaseStats:", error);
    throw new HttpsError("internal", error.message);
  }
});
