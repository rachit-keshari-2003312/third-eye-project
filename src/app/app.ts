import { Component, OnInit } from '@angular/core';
import { Router, NavigationEnd, RouterOutlet, RouterLink } from '@angular/router';
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
  imports: [CommonModule, RouterOutlet, FormsModule, RouterLink],
  templateUrl: './app.html',
  styleUrls: ['./app.scss']
})
export class AppComponent implements OnInit {
  title = 'Third-Eye - Agentic AI Platform';
  
  // Authentication state (set to true for demo purposes)
  isAuthenticated = true;
  currentUser: User | null = { email: 'demo@thirdeye.ai', apiKey: 'demo-key', name: 'Demo User' };
  
  // UI state
  sidebarCollapsed = false;
  eyeBlinking = false;
  currentRoute = 'conversations';
  searchQuery = '';
  selectedTab = 'conversations';
  
  // Login form
  loginForm: LoginForm = {
    email: '',
    apiKey: ''
  };

  // Navigation items
  navigationItems = [
    { route: 'conversations', label: 'Conversations', icon: '💬' },
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
          this.currentUser = user;
          this.isAuthenticated = true;
        } catch (error) {
          console.error('Error parsing stored user:', error);
          localStorage.removeItem('thirdEyeUser');
        }
      }
    }
  }

  private startEyeBlinking() {
    setInterval(() => {
      this.eyeBlinking = true;
      setTimeout(() => {
        this.eyeBlinking = false;
      }, 150);
    }, 3000 + Math.random() * 2000); // Random interval between 3-5 seconds
  }

  private updateCurrentRoute(url: string) {
    const route = url.split('/')[1] || 'conversations';
    this.currentRoute = route;
    this.selectedTab = route;
  }

  // Navigation methods
  navigateTo(route: string) {
    console.log('🔄 Navigation clicked:', route);
    console.log('🔄 Current URL:', this.router.url);
    console.log('🔄 Is authenticated:', this.isAuthenticated);
    
    // Update selected tab immediately for UI feedback
    this.selectedTab = route;
    this.currentRoute = route;
    
    // For demo purposes, allow navigation even without authentication
    this.router.navigate([route]).then(success => {
      console.log('✅ Navigation result:', success);
      console.log('🔄 New URL:', this.router.url);
    }).catch(error => {
      console.error('❌ Navigation error:', error);
    });
  }
  
  // Alternative tab switching method
  switchTab(tabName: string) {
    console.log('🔄 Switching to tab:', tabName);
    this.selectedTab = tabName;
    this.currentRoute = tabName;
    
    // Force navigation
    this.router.navigateByUrl('/', { skipLocationChange: true }).then(() => {
      this.router.navigate([tabName]);
    });
  }

  toggleSidebar() {
    this.sidebarCollapsed = !this.sidebarCollapsed;
  }

  getPageTitle(): string {
    const route = this.currentRoute;
    const navItem = this.navigationItems.find(item => item.route === route);
    return navItem ? navItem.label : 'Dashboard';
  }

  getUserInitials(): string {
    const user = this.currentUser;
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
      this.currentUser = user;
      this.isAuthenticated = true;

      // Reset form
      this.loginForm = { email: '', apiKey: '' };

      // Navigate to conversations
      this.router.navigate(['/conversations']);
    } else {
      alert('Please enter a valid email and API key (minimum 8 characters)');
    }
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
}