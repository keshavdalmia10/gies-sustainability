import { useState, useEffect } from 'react';

// Custom event name
const VALIDATION_EVENT = 'impact-validated';

interface ValidationEventDetail {
  count: number;
  status: 'approved' | 'rejected';
  points?: number;
}

export function useImpactDetective() {
  const [validationCount, setValidationCount] = useState(0);
  const [showToast, setShowToast] = useState(false);
  const [lastAction, setLastAction] = useState<'approved' | 'rejected' | null>(null);
  const [pointsEarned, setPointsEarned] = useState(0);

  // Load initial count from localStorage
  useEffect(() => {
    const savedCount = localStorage.getItem('impact_validation_count');
    if (savedCount) {
      setValidationCount(parseInt(savedCount, 10));
    }
  }, []);

  // Listen for validation events (to update count/toast across components)
  useEffect(() => {
    const handleValidation = (event: Event) => {
      const customEvent = event as CustomEvent<ValidationEventDetail>;
      setValidationCount(customEvent.detail.count);
      setLastAction(customEvent.detail.status);
      setPointsEarned(customEvent.detail.points || 0);
      
      // Show toast
      setShowToast(true);
      setTimeout(() => setShowToast(false), 3000);
    };

    window.addEventListener(VALIDATION_EVENT, handleValidation);
    return () => window.removeEventListener(VALIDATION_EVENT, handleValidation);
  }, []);

  const validateCard = async (status: 'approved' | 'rejected', cardId?: string) => {
    const newCount = validationCount + 1;
    setValidationCount(newCount);
    localStorage.setItem('impact_validation_count', newCount.toString());

    // Dispatch event to notify other components
    const event = new CustomEvent<ValidationEventDetail>(VALIDATION_EVENT, {
      detail: { count: newCount, status }
    });
    window.dispatchEvent(event);

    // Call Backend API
    if (cardId) {
      try {
        // Generate a random visitor ID if not exists
        let visitorId = localStorage.getItem('visitor_id');
        if (!visitorId) {
          visitorId = Math.random().toString(36).substring(7);
          localStorage.setItem('visitor_id', visitorId);
        }

        const response = await fetch(`http://localhost:8000/api/v1/impact-cards/${cardId}/validate`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            visitor_id: visitorId,
            status: status
          }),
        });
        
        if (response.ok) {
          const data = await response.json();
          if (data.points_awarded > 0) {
            // Dispatch event with points
            const event = new CustomEvent<ValidationEventDetail>(VALIDATION_EVENT, {
              detail: { count: newCount, status, points: data.points_awarded }
            });
            window.dispatchEvent(event);
            return; // Exit early as we dispatched a new event
          }
        }
      } catch (error) {
        console.error('Failed to record validation:', error);
      }
    }
  };

  return {
    validationCount,
    showToast,
    lastAction,
    pointsEarned,
    validateCard
  };
}
