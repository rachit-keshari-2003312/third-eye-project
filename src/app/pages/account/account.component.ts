import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-account',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="account-container">
      <div class="account-header">
        <h1>Account Settings</h1>
        <p>Manage your profile and preferences</p>
      </div>
      
      <div class="account-sections">
        <div class="account-card">
          <h2>Profile</h2>
          <div class="profile-info">
            <div class="avatar">👤</div>
            <div class="user-details">
              <h3>John Doe</h3>
              <p>john.doe@example.com</p>
            </div>
          </div>
        </div>
        
        <div class="account-card">
          <h2>API Configuration</h2>
          <div class="api-settings">
            <div class="setting-item">
              <label>AWS Access Key</label>
              <input type="password" value="AKIA..." readonly>
            </div>
            <div class="setting-item">
              <label>Default Region</label>
              <select>
                <option>us-east-1</option>
                <option>us-west-2</option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .account-container {
      max-width: 800px;
      margin: 0 auto;
    }
    
    .account-header {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 30px;
      border-radius: 20px;
      margin-bottom: 30px;
      text-align: center;
    }
    
    .account-sections {
      display: grid;
      gap: 25px;
    }
    
    .account-card {
      background: rgba(255, 255, 255, 0.95);
      padding: 30px;
      border-radius: 16px;
      backdrop-filter: blur(20px);
    }
    
    .profile-info {
      display: flex;
      align-items: center;
      gap: 20px;
    }
    
    .avatar {
      width: 80px;
      height: 80px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 2rem;
      color: white;
    }
    
    .setting-item {
      margin-bottom: 20px;
    }
    
    .setting-item label {
      display: block;
      margin-bottom: 8px;
      font-weight: 600;
    }
    
    .setting-item input,
    .setting-item select {
      width: 100%;
      padding: 12px;
      border: 2px solid #e0e0e0;
      border-radius: 8px;
    }
  `]
})
export class AccountComponent {}
