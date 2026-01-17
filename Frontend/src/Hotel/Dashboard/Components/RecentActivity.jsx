// RecentActivity.jsx
import React from "react";

const RecentActivity = () => {
  const activities = [
    { 
      time: "12:00 PM", 
      title: "Conference Room B Ready", 
      desc: "Room set for 10 AM meeting, with AV and refreshments.", 
      badge: "Popular",
      badgeType: "success"
    },
    { 
      time: "11:00 AM", 
      title: "Room 204 Prepared", 
      desc: "Room cleaned and prepped for new guests.", 
      badge: "Regular",
      badgeType: "primary"
    },
    { 
      time: "10:00 AM", 
      title: "Maintenance Logged", 
      desc: "Toilet issue in Room 109, technician assigned.", 
      badge: "Regular",
      badgeType: "primary"
    },
    { 
      time: "10:00 AM", 
      title: "Guest Checked-In", 
      desc: "Angus Copper checked in a guest, room key issued.", 
      badge: "Regular",
      badgeType: "primary"
    },
    { 
      time: "9:30 AM", 
      title: "Breakfast Service", 
      desc: "Breakfast buffet served for 120 guests.", 
      badge: "Regular",
      badgeType: "primary"
    }
  ];

  return (
    <div className="card">
      <div className="card-header-inline">
        <h4>Recent Activities (1,242)</h4>
        <span className="more">⋯</span>
      </div>
      <ul className="activity-list">
        {activities.map((activity, index) => (
          <li key={index}>
            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
                <span style={{ fontWeight: '700', color: 'var(--text-primary)' }}>{activity.title}</span>
                <span 
                  className={`activity-badge ${activity.badgeType}`}
                  style={{ 
                    background: activity.badgeType === 'success' ? 'var(--success-light)' : 'var(--primary-lightest)',
                    color: activity.badgeType === 'success' ? 'var(--success-color)' : 'var(--primary-color)',
                    padding: '4px 12px',
                    borderRadius: '20px',
                    fontSize: '0.75rem',
                    fontWeight: '700'
                  }}
                >
                  {activity.badge}
                </span>
              </div>
              <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)', lineHeight: '1.4' }}>
                {activity.desc}
              </div>
            </div>
            <span className="activity-time">{activity.time}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default RecentActivity;
