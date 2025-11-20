import { Component, OnInit, signal } from '@angular/core';
import { Router, NavigationEnd, RouterOutlet } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { filter } from 'rxjs/operators';

interface User {
  email: string;
  apiKey: string;
  name?: string;
}

interface LoginForm {
  email: string;
  apiKey: string;
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterOutlet, FormsModule],
  templateUrl: './app.html',
  styleUrls: ['./app.scss']
})
export class AppComponent implements OnInit {
  title = 'Third-Eye - Agentic AI Platform';
  
  // Authentication state (set to true for demo purposes)
  isAuthenticated = signal(true);
  currentUser = signal<User | null>({ email: 'demo@thirdeye.ai', apiKey: 'demo-key', name: 'Demo User' });
  
  // UI state
  sidebarCollapsed = signal(false);
  eyeBlinking = signal(false);
  currentRoute = signal('dashboard');
  searchQuery = signal('');
  
  // Login form
  loginForm: LoginForm = {
    email: '',
    apiKey: ''
  };

  // Navigation items
  navigationItems = [
    { route: 'dashboard', label: 'Dashboard', icon: '📊' },
    { route: 'agents', label: 'AI Agents', icon: '🤖' },
    { route: 'library', label: 'Library', icon: '📚' },
    { route: 'conversations', label: 'Conversations', icon: '💬' },
    { route: 'integrations', label: 'Integrations', icon: '🔗', badge: 'Beta' },
    { route: 'bedrock', label: 'AWS Bedrock', icon: '☁️' },
    { route: 'analytics', label: 'Analytics', icon: '📈' }
  ];

  constructor(private router: Router) {
    // Check if user is already authenticated
    this.checkAuthentication();
    
    // Set up eye blinking animation
    this.startEyeBlinking();
    
    // Listen to route changes
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe((event: NavigationEnd) => {
      console.log('🔄 Route changed to:', event.url);
      this.updateCurrentRoute(event.url);
    });
  }

  ngOnInit() {
    // Initial route setup
    this.updateCurrentRoute(this.router.url);
  }

  private checkAuthentication() {
    if (typeof window !== 'undefined' && window.localStorage) {
      const storedUser = localStorage.getItem('thirdEyeUser');
      if (storedUser) {
        try {
          const user = JSON.parse(storedUser);
          this.currentUser.set(user);
          this.isAuthenticated.set(true);
        } catch (error) {
          console.error('Error parsing stored user:', error);
          localStorage.removeItem('thirdEyeUser');
        }
      }
    }
  }

  private startEyeBlinking() {
    setInterval(() => {
      this.eyeBlinking.set(true);
      setTimeout(() => {
        this.eyeBlinking.set(false);
      }, 150);
    }, 3000 + Math.random() * 2000); // Random interval between 3-5 seconds
  }

  private updateCurrentRoute(url: string) {
    const route = url.split('/')[1] || 'dashboard';
    this.currentRoute.set(route);
  }

  // Navigation methods
  navigateTo(route: string) {
    console.log('🔄 Navigation clicked:', route);
    console.log('🔄 Current URL:', this.router.url);
    console.log('🔄 Is authenticated:', this.isAuthenticated());
    
    // For demo purposes, allow navigation even without authentication
    this.router.navigate([route]).then(success => {
      console.log('✅ Navigation result:', success);
      console.log('🔄 New URL:', this.router.url);
    }).catch(error => {
      console.error('❌ Navigation error:', error);
    });
  }

  toggleSidebar() {
    this.sidebarCollapsed.update(collapsed => !collapsed);
  }

  getPageTitle(): string {
    const route = this.currentRoute();
    const navItem = this.navigationItems.find(item => item.route === route);
    return navItem ? navItem.label : 'Dashboard';
  }

  getUserInitials(): string {
    const user = this.currentUser();
    if (!user) return 'U';
    
    if (user.name) {
      return user.name.split(' ')
        .map(name => name.charAt(0))
        .join('')
        .toUpperCase()
        .substring(0, 2);
    }
    
    return user.email.charAt(0).toUpperCase();
  }

  // Authentication methods
  login() {
    if (!this.loginForm.email || !this.loginForm.apiKey) {
      alert('Please fill in all fields');
      return;
    }

    // Simple validation - in a real app, you'd validate against a backend
    if (this.isValidEmail(this.loginForm.email) && this.loginForm.apiKey.length >= 8) {
      const user: User = {
        email: this.loginForm.email,
        apiKey: this.loginForm.apiKey,
        name: this.extractNameFromEmail(this.loginForm.email)
      };

      // Store user data
      if (typeof window !== 'undefined' && window.localStorage) {
        localStorage.setItem('thirdEyeUser', JSON.stringify(user));
      }
      this.currentUser.set(user);
      this.isAuthenticated.set(true);

      // Reset form
      this.loginForm = { email: '', apiKey: '' };

      // Navigate to dashboard
      this.router.navigate(['/dashboard']);
    } else {
      alert('Please enter a valid email and API key (minimum 8 characters)');
    }
  }

  logout() {
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.removeItem('thirdEyeUser');
    }
    this.currentUser.set(null);
    this.isAuthenticated.set(false);
    this.router.navigate(['dashboard']);
  }

  closeLoginModal(event: Event) {
    // Only close if clicking on the overlay, not the modal content
    if (event.target === event.currentTarget) {
      // For demo purposes, we won't actually close it since login is required
      // In a real app, you might have a guest mode or different behavior
    }
  }

  private isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  private extractNameFromEmail(email: string): string {
    const username = email.split('@')[0];
    return username.split('.').map(part => 
      part.charAt(0).toUpperCase() + part.slice(1)
    ).join(' ');
  }

  // Demo function to toggle authentication for testing
  toggleAuthDemo() {
    if (this.isAuthenticated()) {
      this.logout();
    } else {
      // Quick demo login
      const demoUser: User = {
        email: 'demo@thirdeye.ai',
        apiKey: 'demo-key-123',
        name: 'Demo User'
      };
      this.currentUser.set(demoUser);
      this.isAuthenticated.set(true);
    }
  }
}